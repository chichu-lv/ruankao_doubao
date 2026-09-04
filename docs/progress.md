# Project progress

## Phase 0 — 豆包真实能力审计

- Status: IN_PROGRESS
- Started: 2026-09-03 (Asia/Shanghai)
- Authority: `01_豆包软考私教系统_Codex开发说明书.md`, `02_交给Codex的总执行指令.md`, `04_验收清单.md`
- Current activity: inspect the real 豆包客户端 and signed-in account, then execute all DB-001—DB-040 checks with evidence.

### Repository initialization

- Governance files and evidence directories: created.
- Git metadata: COMPLETE — initialized as an empty repository on branch `main` after the user requested a retry on 2026-09-03.

### Evidence-backed results to date

- Real Doubao client/account/version inspected.
- Private minimal skill created; automatic and explicit invocation passed.
- Exact generated skill file and provenance captured.
- Custom-connector UI and existing Baidu connector inspected; runtime connector calls remain incomplete.
- Authorized local PDF read passed with an exact marker match.
- Signed-in Feishu document, spreadsheet, and multidimensional-table write paths exercised; Doubao access to the same state remains incomplete.
- User-designated Baidu course scopes located; course player opened; time seeking/progress extraction incomplete.
- Logged-in 芝士架构 progress and navigation entries read without answering or submitting questions.
- Scheduler, partner, cross-device, privacy, and diagnostic surfaces inspected.
- Capability matrix and provisional ADR-001 created.

### Current gate blockers

- Prove a state layer readable and writable by Doubao and scheduled tasks.
- Execute one-time, daily, and weekly schedule tests.
- Complete a post-submission result or official export import from 芝士架构.
- Obtain the user's privacy-setting choice before sensitive uploads.

### Exit criteria

- Complete capability matrix with status, version, identity, steps, evidence, limitations, architecture impact, fallback, and issue IDs.
- Preserve screenshots or logs for every conclusion.
- Obtain a minimal skill sample from the current UI; do not invent platform syntax.
- Record runtime/storage/connector decisions in ADR-001.
- Demonstrate a feasible path for every decision gate in specification section 7.3.
