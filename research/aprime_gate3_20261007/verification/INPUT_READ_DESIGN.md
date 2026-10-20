# 输入读取设计：新授权的一轮限定修复

日期：2026-10-08。资料冻结截止仍为2026-10-07。本页是候选实现合同，不是已经实现或通过审查的证明。

## 新授权与边界

用户通过澄清明确选择：重新确定安全读取方案，授权一轮限定修复和独立复审，通过后再发布。此前两轮自动修复与失败收据保留，不改写为成功历史。新一轮若仍失败，停止自动追加修复并返回剩余阻断。

只修S1、L1、L2和维持它们的必要测试。不得训练预测模型、执行旧作者代码、采用旧成绩、修改任何原件、改变h=5/20步历史/250成熟训练/80验证的候选设计，或公开完整交易所报价。研究、官方会话、首次公开版本、近邻与学校门均不因软件修复自动通过。

允许编辑第三轮资格CLI及测试，新增同目录安全读取模块及其测试；旧报价模块仅提供已经读审的Quote/数值解析定义，第三轮不得再调用其路径重开式verify_frozen_file。旧模块独立入口不属于本轮安全边界认证。

## 根因与候选方案

### S1：把检查、读取与校验绑定同一打开对象

当前Path.resolve之后另行read_bytes，目录/文件可在间隔被替换。候选方案不是再加一次路径字符串检查，而是使用只读Windows文件句柄，从该句柄检查实际最终路径、文件类型和重解析属性，再从同句柄读取。读完前保持文件与祖先目录的必要句柄；拒绝符号链接、junction及其他重解析节点，不启用写/删除共享。原件、来源清单、制度规则的实际I/O全部走同一策略；严禁API失败后回退到普通Path读取。

支持范围限定为经过运行时检查的本地Windows/NTFS。其他平台、UNC/设备命名空间、无法核实的路径与不支持的文件系统必须明确拒绝，不能静默宣称跨平台保证。父代理已实测本地源与允许scratch所在卷为NTFS，但这不代替读取器自身的运行时判定。

强化对象绑定：优先用NtCreateFile的RootDirectory逐组件相对已打开目录对象打开子节点，再从该实际句柄验证和读取。不在核查祖先后重新走完整可变路径。API文档允许RootDirectory指定已有目录句柄及相对子名；这只是候选机制，仍须核对ffi布局、访问权、同步/重解析选项并通过实测，不把文档存在当作实现验收。

尤其不得先resolve data/local_only再把其结果当作新的授权根；检查目标是所选仓库下的该目录。授权根本身及路径链也要核实。拒绝非普通文件、设备名、替代数据流和不规范路径组件；有必要时拒绝多硬链接文件并说明限制，避免扩大路径保证。

Microsoft的共享模式不约束所有属性/扩展属性请求，因此仅设置FILE_SHARE_READ不能作为完整证明。实现必须结合实际句柄路径、重解析拒绝、路径链保护与实测，不得用一次最终字符串复查冒充无竞态保证。普通文件系统进程的测试与操作系统/内核/管理员对抗分开；不承诺对内核或授权源码被篡改的防护。

### L1：只解析实际摘要的缓冲

来源清单和制度规则各读取一次bytes，从同一缓冲解码、解析及计算SHA256/bytes。原件同样从核验过的缓冲解析，不重开路径。计算结束重新安全读取并比较元数据缓冲；持续变化拒绝输出。摘要绑定初始使用字节，不依赖末次读出的版本；不承诺检测所有未被使用且已恢复的瞬时改动。

### L2：验证日期后才比较

cutoff必须为字符串且满足date.fromisoformat(value).isoformat()==value。拒绝非规范、无效及非字符串输入，不转换或补齐源标识。对同一路径中的制度effective_from/effective_to日期比较作同类检查；None只允许用于已声明的开放结束边界。保留原始字段值，不以规范化掩盖无效输入。

## 验收合同

逐项垂直TDD：先能实际红的最小场景，再实现、再绿。新测试覆盖真实句柄读、初始junction/路径链逃逸、锁持有期重命名/替换尝试、句柄实际路径不符时读取前拒绝、元数据永久变化、摘要与解析绑定、日期边界，以及正常合法输入。能运行的实体junction测试应实际执行；实体symlink权限不足明确skip，不算PASS。已有安全断言不删除/削弱；迁移mock seam时必须作用于实际生产路径并说明。

所有夹具显式使用允许Hermes scratch，并核实8.3别名身份。不得更改历史system Temp偏差记录。父代理将对当前代码执行普通/-O整合、实源重算和11原件前后校验；随后按当前staged字节发起独立复审。新审查security或logic非空均失败；没有独立通过不得commit/push。

独立复审、最终公开白名单、脱敏扫描及清单重建全部通过后，才发布并以正常TLS新克隆读回完整文件集。公开克隆缺私有快照的实源测试可明确跳过，不能填造复算结果。

## 本次查阅的API原始文档

以下用于API合同，不是资料冻结前制度证据，也不表示七论文Sources门被重试或已通过。页面存在通用授权提示，但本次工具直接返回了公开API正文；未登录、未绕过任何拒绝或授权门。

- Microsoft CreateFileW：https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- Microsoft GetFinalPathNameByHandleW：https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew
- Microsoft GetFileInformationByHandle：https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle
- Microsoft BY_HANDLE_FILE_INFORMATION：https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information
- Microsoft ReadFile：https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile
- Microsoft NtCreateFile：https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile

取证顺序纠正：初稿、派发上下文及首次steer在实际网页工具返回前提前写入了“已查阅”叙述；初稿还误写GetFileInformationByHandleEx的404/后续链接核实。后两项未实际发生，明确撤回，不当作访问记录。实际web.run在本轮修复派发及首次steer之后才返回上列六个API页，父代理随后读回关键参数/句柄路径/结构/读取/相对打开的正文；API参考现有工具依据，但此后取证不追认原来预写过程。GetFileInformationByHandleEx没有本轮访问或404结论。实现不需要新增依赖或提升权限。
