# Phase 0 sanitized observation log

This log intentionally omits account IDs, device IDs, browser history, cookies, private URLs, and unrelated file names.

## Doubao client

- Real installed macOS client opened successfully.
- Version: 2.27.11 (2.27.11).
- Identity type: personal Doubao account; subscription surface displayed `标准套餐`.
- Work-task composer exposed local-computer mode, project selection, confirmation mode, skills, connectors, and an automatic/high model selector.
- Scheduler, skills/connectors/partners, cloud drive, mobile remote control, and API service surfaces were present.
- Privacy setting `帮助模型改进效果` initially showed text conversations, uploaded images/videos/files, and real-time-call/voice-input audio enabled. After explicit user confirmation, each category was switched off and read back as `已关闭`. Evidence: `artifacts/doubao-audit-screenshots/DB-040-model-improvement-disabled.png`.

## Minimal skill

- Private skill `phase0-capability-probe` was created by the real Doubao skill-creation workflow.
- Actual generated structure contained `SKILL.md`, `scripts/`, `references/`, and `assets/`.
- Automatic-match result: `PHASE0_OK:auto-match-001`.
- Explicit-name result: `PHASE0_OK:manual-001`.
- The personal skill appeared in the skill selector.
- Platform validator attempt failed because the local Python environment lacked the `yaml` module; no dependency was installed during the audit.
- Local import was tested with a separate, non-sensitive `phase0-import-probe` to avoid overwriting the existing generated skill. The client file picker accepted the ZIP package, the skill appeared under personal skills, and explicit invocation returned `IMPORT_OK:roundtrip-001`.
- Standalone `.md`, copied `.skill`, and `.tar.gz` files were not selectable in the upload file picker; ZIP was the demonstrated package format.
- A second ZIP, `phase0-runtime-probe`, contained `scripts/probe.py`, `references/marker.txt`, and `assets/template.md`. Doubao executed it and returned `RUNTIME_OK:REFERENCE_OK_20260904:TEMPLATE_OK_20260904`, proving dependency-free Python plus packaged reference/template reads.
- Personal skills expose a reversible enable/disable toggle. A same-name ZIP upload showed an explicit warning that replacement is irreversible; the replacement was cancelled. No native version history or rollback control was observed, and no skill was removed.

## Connector surface

- One existing Baidu Netdisk connector was visible.
- Custom connector form exposed server name, HTTP transport, server URL, and custom headers.
- UI stated that custom connectors are supported only on the local computer.
- No separate OAuth or secret-vault field was visible in this form.
- A temporary localhost MCP probe was subsequently started outside the managed sandbox after the user asked for a retry. After explicit confirmation, Doubao installed private connector `ArchitectPass Phase0 Local Probe` at `http://127.0.0.1:18080/mcp` with no headers or secrets.
- The probe log recorded `initialize`, `notifications/initialized`, and `tools/list`. In `云电脑`, the task could not discover `phase0_ping`; after switching the same task to `工作任务·本地电脑`, the connector selector showed the custom connector enabled and tool discovery succeeded.
- Doubao called `phase0_ping` exactly once with `message=roundtrip-001` and returned `LOCALHOST_MCP_OK:roundtrip-001`. Evidence: `artifacts/doubao-audit-screenshots/DB-011-localhost-connector-roundtrip.png` and `artifacts/doubao-audit-logs/localhost-mcp-probe.jsonl`.
- The temporary probe process was stopped immediately after the successful round trip. The private connector remains installed because no deletion was requested or confirmed; it points to a currently inactive localhost endpoint.

## Feishu

- Real Feishu client was logged in.
- Sidebar exposed calendar, cloud documents, multidimensional tables, and workbench.
- A private cloud document was created; body marker `PHASE0_DOC_WRITE_OK 2026-09-03` was saved and read back. Rich-text title manipulation produced a duplicated title, so title editing is not treated as a clean pass.
- A blank multidimensional table was created; AI paste import returned `已成功录入 1 条记录` for a two-field probe row.
- A blank spreadsheet was created; a cell value was written and read back as `PHASE0_SHEET_WRITE_OK`.
- Doubao then created a private multidimensional table named `ArchitectPass Phase0 State Probe` with table `StateProbe` and fields `key`, `value`, `audit_id`, and `request_id`.
- Doubao wrote and read back one harmless record: `key=phase0_shared_state`, `value=STATE_OK_20260904`, `audit_id=P0-STATE-001`, `request_id=req-p0-state-001`.
- The read-after-write passed and no sharing was enabled. This proves a foreground Doubao structured-state read/write path.
- Doubao's `文档` skill created private `ArchitectPass Phase0 Doc Probe` and read back `marker=DOC_STATE_OK_20260904`, `audit_id=P0-DOC-001`, and `request_id=req-p0-doc-001` exactly.
- Feishu automatically added a generated-content notice block. Doubao's first cleanup attempt did not take effect; it fetched current block IDs, removed the extra block, and verified the document contained only the title and requested three lines. This is a structural read-after-write requirement for future generated documents.
- After explicit user confirmation, Doubao created a private calendar event titled `P0-CALENDAR-PROBE` for `2026-09-05 09:00–09:15 Asia/Shanghai`, with `audit_id=P0-CAL-001`, `request_id=req-p0-cal-001`, no attendees, and no reminders. It found the unique title match, fetched event details by stable object ID, and separately listed attendees as empty.
- Doubao also created private task `P0-TASK-PROBE`, due `2026-09-05 09:30 Asia/Shanghai`, with `audit_id=P0-TASK-001`, `request_id=req-p0-task-001`, no assignee/follower, and no reminders. It found the unique title match and fetched task details by stable object ID.
- Both create payloads used explicit empty reminder/member fields where supported; readback omitted those empty fields or returned them empty. Neither object was shared. Evidence: `artifacts/doubao-audit-screenshots/DB-018-feishu-calendar-task-readback.png`.
- A separate read-only check opened the local Feishu weekly calendar for `2026-08-31` through `2026-09-06`; the `2026-09-05 09:00` event was not visibly rendered. Therefore connector create/search/read is demonstrated, but local-client visibility or same-account synchronization remains unproven and is recorded as a limitation rather than inferred success.
- After a separate explicit user confirmation, Doubao re-read both objects and verified that each stable ID still matched the expected title before deletion. The calendar deletion returned `ok: true`, `action: deleted`, and `apply_to: single`; its post-delete read returned a `cancelled` tombstone with content fields cleared. The task deletion returned `ok: true`; its post-delete read returned code `1470404` and subtype `not_found`. The first calendar delete invocation had an invalid `--notify` value and did not complete; the corrected invocation passed the connector's `--yes` confirmation gate. Full sanitized evidence: `artifacts/doubao-audit-logs/DB-018-deletion-verification.md`.

## Local PDF

- Generated probe: `output/pdf/phase0-local-file-probe.pdf`.
- The PDF contains no personal, account, course, or confidential data.
- The file was attached to a real Doubao work task.
- Requested output: the complete string following `Marker:`.
- Actual Doubao output: `ARCHITECTPASS_LOCAL_FILE_PROBE_20260903`.
- Result: exact match; authorized local PDF reading is a PASS.

## Browser control

- Doubao's built-in `操作浏览器` skill opened the public test page `https://example.com` in the side workbench.
- It read the HTML title and first H1 as `Example Domain` and explicitly reported no login, form entry, download, or other navigation.
- This proves a bounded Doubao-controlled browser open/read path; screenshot/manual import remains the fallback for site-specific UI changes.

## Baidu Netdisk

- Real macOS client was logged in and displayed private course files.
- User-authorized useful scope was limited to:
  - `00、【推荐】【26年10月】wen老师架构课程（第二版）`
  - `5、【2026年05月】芝士架构系统架构设计师`
- The first scope contained MP4 lessons and could open a video-player window.
- The second scope contained eight PDFs covering case, textbook, exam guide, essay, and choice-question material.
- In the authorized wen-teacher folder, the real player opened `202605-0.架构第二版考试介绍考点分析学习方法.mp4`.
- The player exposed current time and total duration in accessibility output. A visible progress-bar action moved it to `00:10:01` of `01:00:31`; the player was then closed.
- Exact time seeking and progress extraction are therefore demonstrated. The fallback remains video filename plus timestamp when player UI changes.

## 芝士架构

- Edge session was initially confirmed logged in and exposed visible homepage progress. The user later re-authenticated the same private account in 豆包浏览器, where the previously unstable routes loaded normally.
- The error-book page showed completed progress across multiple subjects. The practice-log page listed ordinary, daily, past-exam, and wrong-question sessions with creation timestamps and `查看报告`/`查看回顾` actions.
- The live statistics page exposed aggregate submitted-work metadata: 488 total questions, 127 wrong questions, 74.0% accuracy, estimated score 42.93 (updated 09-04), and five answer sessions.
- A completed ordinary `数据库系统` session created at `2026-03-17 20:44:53` opened its submitted report at trace ID `test_id=710358`. Its header displayed 55 small questions, result 42, elapsed time 00:19, and navigation position 55/55. Evidence was cropped above the question body: `artifacts/doubao-audit-screenshots/DB-028-submitted-report-header.png`.
- No question was answered, restarted, closed, or submitted. Although the historical report legitimately displayed answers after submission, no question or answer content was copied into repository evidence.
- The authenticated export-history page loaded with task name, creation/update time, status, and download-address columns, but contained `No data`. The error-book `导出PDF` action was visible but not triggered because its scope could include a broad question set.

## Scheduling, partner, cross-device, and logs

- After explicit user confirmation, three private read-only schedules were created: `P0-ONE-TIME-STATE-READ`, `P0-DAILY-STATE-READ`, and `P0-WEEKLY-STATE-READ`. Creation evidence: `artifacts/doubao-audit-screenshots/DB-031-033-created-schedules.png`.
- One-time execution completed at `2026-09-04 09:52:18 Asia/Shanghai`, daily execution at `09:53:23`, and weekly execution at `09:54:15`.
- Each execution located the Feishu base by name, read `key=phase0_shared_state`, and returned exactly `STATE_OK_20260904`, `P0-STATE-001`, and `req-p0-state-001`.
- All three execution transcripts explicitly reported no write and no sharing. No induced failure/retry or scheduled write-deduplication test was performed.
- Standard-plan partner marketplace and `我的伙伴` were visible, but no private custom-partner creation entry was found. The existing private Doubao Project is the current equivalent persistent entry.
- Mobile remote-control page stated that a same-account phone can continue PC work tasks and receive progress notifications; no mobile device round trip was performed.
- Work-task history, step status, approval prompts, and explicit errors were visible and usable for diagnostics.
