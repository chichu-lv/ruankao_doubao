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
- Local ZIP skill import passed with a separate canary; its explicit invocation returned `IMPORT_OK:roundtrip-001`.
- A packaged runtime probe read `references/` and `assets/` and ran a dependency-free Python script successfully.
- Private custom localhost connector installed after explicit confirmation; its MCP handshake and one exact read-only call passed in local-computer mode. Cloud-computer mode could not discover it, confirming the product's local-only boundary.
- Authorized local PDF read passed with an exact marker match.
- Doubao created, wrote, and read a private Feishu multidimensional table containing a harmless state marker plus audit/request IDs.
- Doubao created and read back a private Feishu document with exact marker/audit/request IDs; the platform's automatic generated-content block required structural cleanup and re-verification.
- After explicit confirmation, Doubao created one private Feishu calendar event and one private Feishu task, located both by title, and independently read them back with exact audit/request IDs and stable object IDs. After a second explicit confirmation, it validated the ID/title pairs, deleted only those two objects, and verified a cancelled calendar tombstone plus task `not_found`. The local Feishu weekly view did not visibly render the event before deletion, so cross-client visibility remains open.
- User-designated Baidu course scopes located and a real course player opened.
- Doubao browser skill opened and read a public test page in its side workbench.
- A real authorized Baidu course video was sought to `00:10:01`, and current/total playback times were read from the player.
- Logged-in 芝士架构 progress and navigation entries read without answering or submitting questions.
- Native one-time, daily, and weekly tasks executed and each read the same Feishu state record.
- Scheduler, partner, cross-device, privacy, and diagnostic surfaces inspected.
- After explicit user confirmation, all three Doubao model-improvement data categories were disabled and read back as closed.
- Capability matrix updated and ADR-001 accepted for the Phase 0 architecture decision.

### Current gate blockers

- Close residual skill lifecycle, trusted-HTTPS/authentication, Feishu calendar client-visibility, limit, and cross-device rows or record final constrained fallbacks.
- Complete a post-submission result or official export import from 芝士架构.

### Exit criteria

- Complete capability matrix with status, version, identity, steps, evidence, limitations, architecture impact, fallback, and issue IDs.
- Preserve screenshots or logs for every conclusion.
- Obtain a minimal skill sample from the current UI; do not invent platform syntax.
- Record runtime/storage/connector decisions in ADR-001.
- Demonstrate a feasible path for every decision gate in specification section 7.3.
