# Phase 0 test record

- Dates: 2026-09-03 to 2026-09-04
- Environment: user's real Mac, real 豆包 account, real installed/browser surfaces
- Status: IN_PROGRESS

## Completed test results

| Test | Result | Evidence |
|---|---:|---|
| Doubao client/account/version | PASS | `artifacts/doubao-audit-screenshots/DB-001-client-version.png` |
| Minimal private skill creation | PASS | `artifacts/doubao-skill-samples/phase0-capability-probe/` and DB-004 screenshots |
| Automatic skill match | PASS | Returned `PHASE0_OK:auto-match-001` |
| Explicit skill call | PASS | Returned `PHASE0_OK:manual-001` |
| Authorized local PDF read | PASS | Returned `ARCHITECTPASS_LOCAL_FILE_PROBE_20260903` |
| Feishu private document body write/read | PASS with title-edit limitation | Sanitized observation log |
| Feishu multidimensional-table row import | PASS | UI reported `已成功录入 1 条记录` |
| Feishu spreadsheet cell write/read | PASS | Read back `PHASE0_SHEET_WRITE_OK` |
| Baidu Netdisk login and target-course lookup | PASS | Sanitized observation log |
| Baidu exact time seek/progress read | INCOMPLETE | DB-024/DB-025 matrix rows |
| 芝士架构 login and visible chapter progress | PASS | Sanitized observation log |
| 芝士架构 post-submission result/export | INCOMPLETE | DB-028/DB-029 matrix rows |
| One-time/daily/weekly schedules | INCOMPLETE | DB-031 to DB-034 matrix rows |

## Safety assertions

- No 芝士架构 question was answered or submitted by automation.
- No answer or explanation was exposed before user submission.
- No private API, DRM, paywall, membership limit, or CAPTCHA was bypassed.
- No password, cookie, OTP, API key, access token, full account ID, or device ID was recorded.
- Three generator placeholder files were deleted only after explicit user confirmation; the empty skill directories were retained.

See `docs/doubao-capability-matrix.md` for all DB-001 through DB-040 statuses and open issue IDs.
