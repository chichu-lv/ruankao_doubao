# Phase 0 sanitized observation log

This log intentionally omits account IDs, device IDs, browser history, cookies, private URLs, and unrelated file names.

## Doubao client

- Real installed macOS client opened successfully.
- Version: 2.27.11 (2.27.11).
- Identity type: personal Doubao account; subscription surface displayed `标准套餐`.
- Work-task composer exposed local-computer mode, project selection, confirmation mode, skills, connectors, and an automatic/high model selector.
- Scheduler, skills/connectors/partners, cloud drive, mobile remote control, and API service surfaces were present.
- Privacy setting `帮助模型改进效果` showed text conversations, uploaded images/videos/files, and voice inputs enabled.

## Minimal skill

- Private skill `phase0-capability-probe` was created by the real Doubao skill-creation workflow.
- Actual generated structure contained `SKILL.md`, `scripts/`, `references/`, and `assets/`.
- Automatic-match result: `PHASE0_OK:auto-match-001`.
- Explicit-name result: `PHASE0_OK:manual-001`.
- The personal skill appeared in the skill selector.
- Platform validator attempt failed because the local Python environment lacked the `yaml` module; no dependency was installed during the audit.

## Connector surface

- One existing Baidu Netdisk connector was visible.
- Custom connector form exposed server name, HTTP transport, server URL, and custom headers.
- UI stated that custom connectors are supported only on the local computer.
- No separate OAuth or secret-vault field was visible in this form.
- Local MCP probe could not be started because the managed execution sandbox denied binding a localhost port. This is an audit-environment blocker, not evidence that Doubao rejects localhost.

## Feishu

- Real Feishu client was logged in.
- Sidebar exposed calendar, cloud documents, multidimensional tables, and workbench.
- A private cloud document was created; body marker `PHASE0_DOC_WRITE_OK 2026-09-03` was saved and read back. Rich-text title manipulation produced a duplicated title, so title editing is not treated as a clean pass.
- A blank multidimensional table was created; AI paste import returned `已成功录入 1 条记录` for a two-field probe row.
- A blank spreadsheet was created; a cell value was written and read back as `PHASE0_SHEET_WRITE_OK`.
- These actions prove the signed-in Feishu account can write. They do not yet prove that Doubao scheduled tasks or connectors can access the same objects.

## Local PDF

- Generated probe: `output/pdf/phase0-local-file-probe.pdf`.
- The PDF contains no personal, account, course, or confidential data.
- The file was attached to a real Doubao work task.
- Requested output: the complete string following `Marker:`.
- Actual Doubao output: `ARCHITECTPASS_LOCAL_FILE_PROBE_20260903`.
- Result: exact match; authorized local PDF reading is a PASS.

## Baidu Netdisk

- Real macOS client was logged in and displayed private course files.
- User-authorized useful scope was limited to:
  - `00、【推荐】【26年10月】wen老师架构课程（第二版）`
  - `5、【2026年05月】芝士架构系统架构设计师`
- The first scope contained MP4 lessons and could open a video-player window.
- The second scope contained eight PDFs covering case, textbook, exam guide, essay, and choice-question material.
- Exact time seeking and stable progress extraction were not proven; fallback is to name the video and timestamp for manual positioning.

## 芝士架构

- Edge session was confirmed logged in by the user and then re-read through the real browser UI.
- Visible homepage progress included nonzero completed counts across multiple chapters.
- Navigation entries for practice logs, past exams, error book, collections, notes, statistics, and one-click export were present.
- No question was answered, submitted, or opened for pre-submission answers.
- Direct navigation to the statistics route left the visible single-page-app content on the homepage in this audit run; result-page and export-file tests remain incomplete.

## Scheduling, partner, cross-device, and logs

- Scheduler UI and templates for recurring work were visible; no real one-time/daily/weekly tasks have yet been created.
- Standard-plan partner marketplace and `我的伙伴` were visible, but no private custom-partner creation entry was found. The existing private Doubao Project is the current equivalent persistent entry.
- Mobile remote-control page stated that a same-account phone can continue PC work tasks and receive progress notifications; no mobile device round trip was performed.
- Work-task history, step status, approval prompts, and explicit errors were visible and usable for diagnostics.
