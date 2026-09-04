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
| Local ZIP skill import and call | PASS | Imported `phase0-import-probe`; returned `IMPORT_OK:roundtrip-001` |
| Skill script/reference/template runtime | PASS | Returned `RUNTIME_OK:REFERENCE_OK_20260904:TEMPLATE_OK_20260904` |
| Skill lifecycle | PARTIAL | Enable/disable and same-name overwrite warning observed; native rollback absent, overwrite/removal not executed |
| Custom localhost connector install/handshake | PASS | `ArchitectPass Phase0 Local Probe` installed after confirmation; server log records `initialize`, `notifications/initialized`, and `tools/list` |
| Local-computer connector call | PASS | `phase0_ping(message=roundtrip-001)` returned `LOCALHOST_MCP_OK:roundtrip-001`; evidence screenshot and server `tools/call` log |
| Cloud-computer use of custom localhost connector | NOT SUPPORTED | Connector was not discoverable in `云电脑`; it appeared enabled and callable after switching the task to `本地电脑` |
| Authorized local PDF read | PASS | Returned `ARCHITECTPASS_LOCAL_FILE_PROBE_20260903` |
| Feishu private document body write/read | PASS with title-edit limitation | Sanitized observation log |
| Doubao-to-Feishu document write/read | PASS with generated-block cleanup | Created private test document; exact marker/audit/request IDs read back |
| Feishu multidimensional-table row import | PASS | UI reported `已成功录入 1 条记录` |
| Feishu spreadsheet cell write/read | PASS | Read back `PHASE0_SHEET_WRITE_OK` |
| Doubao-to-Feishu structured-state write/read | PASS | Created private `ArchitectPass Phase0 State Probe`; read back `STATE_OK_20260904`, `P0-STATE-001`, and `req-p0-state-001` |
| Doubao-to-Feishu calendar event create/search/read | PASS via connector; client visibility unresolved | Created private `P0-CALENDAR-PROBE` for 2026-09-05 09:00–09:15 Asia/Shanghai with no attendees/reminders; search and separate detail/attendee reads matched audit/request IDs and stable object ID. Local Feishu weekly view did not visibly render it. |
| Doubao-to-Feishu task create/search/read | PASS | Created private `P0-TASK-PROBE`, due 2026-09-05 09:30 Asia/Shanghai with no assignee/follower/reminder; separate search/detail reads matched audit/request IDs and stable object ID. Evidence: `artifacts/doubao-audit-screenshots/DB-018-feishu-calendar-task-readback.png`. |
| Feishu calendar/task cleanup with exact-ID guard | PASS | After separate explicit confirmation, both ID/title pairs matched before deletion. Calendar delete returned `action: deleted` and post-read `status: cancelled` with cleared content; task post-read returned code `1470404`, subtype `not_found`. Evidence: `artifacts/doubao-audit-logs/DB-018-deletion-verification.md`. |
| Baidu Netdisk login and target-course lookup | PASS | Sanitized observation log |
| Doubao browser open/read | PASS | Opened `example.com`; title and H1 both read as `Example Domain` |
| Baidu exact time seek/progress read | PASS | Authorized course video sought to `00:10:01`; total `01:00:31` |
| 芝士架构 login and visible chapter progress | PASS | Sanitized observation log |
| 芝士架构 post-submission result/export | INCOMPLETE | DB-028/DB-029 matrix rows |
| One-time schedule reads shared state | PASS | Executed 2026-09-04 09:52:18 Asia/Shanghai; sanitized observation log |
| Daily schedule reads shared state | PASS | Executed 2026-09-04 09:53:23 Asia/Shanghai; sanitized observation log |
| Weekly schedule reads shared state | PASS | Executed 2026-09-04 09:54:15 Asia/Shanghai; sanitized observation log |
| Scheduled failure/retry and write deduplication | INCOMPLETE | DB-034 matrix row |
| Model-improvement privacy controls | PASS | After explicit confirmation, text conversations, uploaded images/videos/files, and real-time-call/voice-input audio were each switched off and read back as `已关闭`. Evidence: `artifacts/doubao-audit-screenshots/DB-040-model-improvement-disabled.png`. |

## Safety assertions

- No 芝士架构 question was answered or submitted by automation.
- No answer or explanation was exposed before user submission.
- No private API, DRM, paywall, membership limit, or CAPTCHA was bypassed.
- No password, cookie, OTP, API key, access token, full account ID, or device ID was recorded.
- Three generator placeholder files were deleted only after explicit user confirmation; the empty skill directories were retained.
- The three test schedules were created only after explicit user confirmation. Their prompts were read-only; no scheduled write or sharing occurred.
- The persistent localhost connector was installed only after explicit user confirmation. It used no secret, was called once read-only, and the temporary localhost server was stopped afterward; the connector itself was not deleted.
- The Feishu calendar event and task were created only after explicit user confirmation, remained private and unshared, and were deleted only after a separate explicit confirmation. Exact IDs and titles were checked before deletion; post-delete reads were recorded.
- The three model-improvement data permissions were changed only after explicit user confirmation; the final UI showed all three disabled.

See `docs/doubao-capability-matrix.md` for all DB-001 through DB-040 statuses and open issue IDs.
