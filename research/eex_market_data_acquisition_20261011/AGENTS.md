# Independent market-data acquisition package

- Keep this work separate from the frozen v8 and v8.1 manuscripts and the original quantity regressions. Acquisition does not authorize model fitting, manuscript replacement or merging into main.
- Publish only real downloaded files with an explicitly recorded redistribution basis. An accessible download URL or a user's publication request does not resolve third-party rights. Keep uncertain exchange snapshots and whole third-party reports private; publish source links, hashes and acquisition instructions instead.
- Preserve original bytes and literal instrument identifiers. Describe author deposits as author-provided data, not automatically as exchange-authenticated originals.
- Daily front-December futures, daily closes, settlement prices, transaction prices and best-bid/ask observations are different measurements. None automatically satisfies the existing auction-close pairing protocol.
- Never fabricate reference rows, fill missing observations with zero, infer the sign of a deviation from its absolute monthly mean, or reverse-engineer event prices from aggregated report tables.
- Record actual retrieval dates separately from source publication dates. Reconcile row/file counts in Python and independently read the files before publication.
- Do not publish local usernames, personal paths, credentials, API keys, cookies or signed access URLs in metadata or reports. Use repository-relative paths and public stable source URLs.
- New verification code must use explicit integrity exceptions and be exercised in normal and optimized Python. Its tests contain synthetic logic fixtures only, never claimed market observations.
- After pushing, fetch and read back the exact commit and compare every new published file byte before claiming delivery. Do not silently overwrite a concurrent remote update.
