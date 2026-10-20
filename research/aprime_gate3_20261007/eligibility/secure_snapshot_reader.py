"""Fail-closed, read-only Windows/local fixed NTFS snapshot input.

No Path-based reopening, credential access or privilege enabling. Attributes
are inspected separately: Windows share flags do NOT lock all attributes/EAs.
This is not protection against administrators, kernel/drivers or edited code.
"""
import ctypes
from ctypes import wintypes as w
import ntpath
import os
from pathlib import Path
import re

GENERIC_READ = 0x80000000
FILE_SHARE_READ = 1
OPEN_EXISTING = 3
OPEN_REPARSE_POINT = 0x00200000
BACKUP_SEMANTICS = 0x02000000
DIRECTORY = 0x10
REPARSE_POINT = 0x400
DEVICE = 0x40
INVALID_HANDLE = ctypes.c_void_p(-1).value


class FileInformation(ctypes.Structure):
    _fields_ = [('attributes', w.DWORD), ('creation', w.FILETIME),
                ('access', w.FILETIME), ('write', w.FILETIME),
                ('volume', w.DWORD), ('size_high', w.DWORD), ('size_low', w.DWORD),
                ('links', w.DWORD), ('index_high', w.DWORD), ('index_low', w.DWORD)]


def _absolute_path(value):
    raw = os.fspath(value)
    if type(raw) is not str or not re.match(r'^[A-Za-z]:[\\/]', raw):
        raise ValueError('Unsafe path: require an absolute local DOS drive path')
    raw = raw.replace('/', '\\')
    if raw.endswith('\\') and len(raw) != 3:
        raise ValueError('Unsafe path: noncanonical trailing separator')
    for component in raw[3:].split('\\') if len(raw) > 3 else ():
        stem = component.split('.')[0].upper()
        if (not component or component in ('.', '..') or component != component.rstrip(' .')
                or any(c in component for c in '<>:"/\\|?*~')
                or any(ord(c) < 32 for c in component)
                or stem in ('CON', 'PRN', 'AUX', 'NUL', 'CLOCK$', 'CONIN$', 'CONOUT$')
                or re.fullmatch(r'(COM|LPT)[1-9¹²³]', stem)):
            raise ValueError('Unsafe path: noncanonical or device component')
    return raw


def validate_root(value):
    return Path(_absolute_path(value))


class _WindowsAPI:
    def __init__(self):
        if os.name != 'nt':
            raise ValueError('Unsafe unsupported platform: Windows fixed NTFS required')
        self.dll = ctypes.WinDLL('kernel32', use_last_error=True)
        signatures = {
            'CreateFileW': ([w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE], w.HANDLE),
            'GetFileInformationByHandle': ([w.HANDLE, ctypes.POINTER(FileInformation)], w.BOOL),
            'GetFinalPathNameByHandleW': ([w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD], w.DWORD),
            'GetFileType': ([w.HANDLE], w.DWORD),
            'GetDriveTypeW': ([w.LPCWSTR], w.UINT),
            'GetVolumeInformationByHandleW': ([w.HANDLE, w.LPWSTR, w.DWORD, ctypes.POINTER(w.DWORD),
                                              ctypes.POINTER(w.DWORD), ctypes.POINTER(w.DWORD), w.LPWSTR, w.DWORD], w.BOOL),
            'ReadFile': ([w.HANDLE, w.LPVOID, w.DWORD, ctypes.POINTER(w.DWORD), w.LPVOID], w.BOOL),
            'CloseHandle': ([w.HANDLE], w.BOOL),
        }
        for name, (args, result) in signatures.items():
            function = getattr(self.dll, name)
            function.argtypes, function.restype = args, result

    def _error(self, operation):
        code = ctypes.get_last_error()
        return ValueError(f'Unsafe input: {operation} failed (Windows error {code})')

    def _open(self, path, directory):
        flags = OPEN_REPARSE_POINT | (BACKUP_SEMANTICS if directory else 0)
        handle = self.dll.CreateFileW('\\\\?\\' + path, GENERIC_READ, FILE_SHARE_READ,
                                      None, OPEN_EXISTING, flags, None)
        if handle is None or handle == INVALID_HANDLE:
            raise self._error('CreateFileW')
        return handle

    def _close(self, handle):
        if not self.dll.CloseHandle(handle):
            raise self._error('CloseHandle')

    def _inspect(self, handle, directory):
        info = FileInformation()
        if not self.dll.GetFileInformationByHandle(handle, ctypes.byref(info)):
            raise self._error('GetFileInformationByHandle')
        if self.dll.GetFileType(handle) != 1:
            raise ValueError('Unsafe input: require ordinary disk objects')
        if info.attributes & (REPARSE_POINT | DEVICE) or bool(info.attributes & DIRECTORY) != directory:
            raise ValueError('Unsafe input: reparse, device or wrong object type')
        if not directory and info.links != 1:
            raise ValueError('Unsafe input: multiple hard links are unsupported')
        identity = (info.volume, info.index_high, info.index_low)
        if not any(identity[1:]):
            raise ValueError('Unsafe input: unavailable NTFS object identity')
        return identity, info.attributes, (info.size_high << 32) | info.size_low

    def _ntfs_volume(self, handle):
        filesystem = ctypes.create_unicode_buffer(32)
        serial, maximum, flags = w.DWORD(), w.DWORD(), w.DWORD()
        if not self.dll.GetVolumeInformationByHandleW(
                handle, None, 0, ctypes.byref(serial), ctypes.byref(maximum),
                ctypes.byref(flags), filesystem, len(filesystem)):
            raise self._error('GetVolumeInformationByHandleW')
        if filesystem.value != 'NTFS':
            raise ValueError('Unsafe unsupported filesystem: fixed NTFS required')
        return serial.value

    def _final_path(self, handle):
        buffer = ctypes.create_unicode_buffer(32768)
        length = self.dll.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
        if not length or length >= len(buffer):
            raise self._error('GetFinalPathNameByHandleW')
        return buffer.value

    def _bind_final_path(self, handle, expected):
        actual = self._final_path(handle)
        if ntpath.normcase(actual) != ntpath.normcase('\\\\?\\' + expected):
            raise ValueError('Unsafe input: final path does not match authorized lexical object')

    def _read_handle(self, handle):
        chunks = []
        buffer = ctypes.create_string_buffer(65536)
        count = w.DWORD()
        while True:
            if not self.dll.ReadFile(handle, buffer, len(buffer), ctypes.byref(count), None):
                raise self._error('ReadFile')
            if not count.value:
                return b''.join(chunks)
            chunks.append(buffer.raw[:count.value])


def secure_read_bytes(authorized_root, path):
    """Read one object; all errors are explicit and never fall back to Path I/O."""
    root, target = _absolute_path(authorized_root), _absolute_path(path)
    if ntpath.commonpath((ntpath.normcase(root), ntpath.normcase(target))) != ntpath.normcase(root) or target == root:
        raise ValueError('Unsafe input: outside the lexical authorized root')
    api = _WindowsAPI()
    if api.dll.GetDriveTypeW(root[:3]) != 3:
        raise ValueError('Unsafe unsupported volume: local fixed disk required')
    chain = [target[:3]]
    for component in target[3:].split('\\')[:-1]:
        chain.append(ntpath.join(chain[-1], component))
    volume = None
    handles = []
    inspected = []
    try:
        # Keep ancestors from the drive root down; do not reopen/rebind authority.
        for directory in chain:
            handle = api._open(directory, True)
            handles.append(handle)
            info = api._inspect(handle, True)
            api._bind_final_path(handle, directory)
            inspected.append((handle, True, info, directory))
            serial = api._ntfs_volume(handle)
            if info[0][0] != serial or (volume is not None and serial != volume):
                raise ValueError('Unsafe input: volume identity mismatch')
            volume = serial
        handle = api._open(target, False)
        handles.append(handle)
        before = api._inspect(handle, False)
        api._bind_final_path(handle, target)
        if before[0][0] != volume or api._ntfs_volume(handle) != volume:
            raise ValueError('Unsafe input: volume identity mismatch')
        inspected.append((handle, False, before, target))
        for held, directory, info, expected in inspected:
            api._bind_final_path(held, expected)
            if api._inspect(held, directory) != info:
                raise ValueError('Unsafe input: path chain changed before handle read')
        body = api._read_handle(handle)
        for held, directory, info, expected in inspected:
            api._bind_final_path(held, expected)
            if api._inspect(held, directory) != info:
                raise ValueError('Unsafe input: path chain changed during handle read')
        if len(body) != before[2]:
            raise ValueError('Unsafe input: object changed during handle read')
        return body
    finally:
        close_error = None
        for handle in reversed(handles):
            try:
                api._close(handle)
            except Exception as error:
                close_error = close_error or error
        if close_error is not None:
            raise close_error
