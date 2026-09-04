# Risk register

| ID | Risk | Status | Mitigation / fallback |
|---|---|---|---|
| R-001 | Current 豆包 account does not expose private custom-partner creation on the observed standard-plan surface. | MITIGATED | Use a private Doubao Project plus private skills as the equivalent persistent entry; re-test after account/client changes. |
| R-002 | Custom `localhost` connectors are unavailable to cloud-computer tasks and may be unavailable to schedules. | PARTIALLY MITIGATED | Real local-computer round trip passed; cloud-computer discovery failed. Keep Feishu as authoritative state, restrict localhost to foreground local tasks, and retain manual fallback. |
| R-003 | 百度网盘 and 芝士架构 UI changes may break browser automation. | OPEN | Version selectors and retain screenshot/export/manual-result fallbacks. |
| R-004 | Audit screenshots may contain account identity or private content. | OPEN | Capture the minimum screen area and redact unnecessary sensitive information before commit or sharing. |
| R-005 | Formal Git metadata initialization was initially blocked by an approval-service 404. | CLOSED | User requested a retry; `git init -b main` then succeeded. |
| R-006 | Feishu client writes may not imply that Doubao or its scheduler can read the same objects. | CLOSED | Doubao created/wrote/read a private multidimensional table; one-time, daily, and weekly tasks read the same record. |
| R-007 | Doubao privacy improvement settings are enabled for text, uploaded files, and voice. | OPEN | Do not transmit sensitive material until the user chooses whether to disable the settings. |
| R-008 | Native schedules may run without the same state, retry, or idempotency guarantees as foreground work. | PARTIALLY MITIGATED | One-time/daily/weekly read paths shared the same state and returned audit/request IDs. Keep scheduled writes disabled until failure/retry and deduplication tests pass. |
| R-009 | Feishu rich-text title editing behaved non-idempotently during the UI probe. | OPEN | Use API/connector operations with idempotency and read-after-write verification; do not bulk-edit through blind UI typing. |
