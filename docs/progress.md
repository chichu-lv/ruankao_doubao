# Project progress

## Phase 0 — 豆包真实能力审计

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-03 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Authority: `01_豆包软考私教系统_Codex开发说明书.md`, `02_交给Codex的总执行指令.md`, `04_验收清单.md`
- Current activity: Phase 0 and Phase 1 closed; prepare Phase 2 incremental material ingestion and traceable retrieval.

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
- Logged-in 芝士架构 aggregate statistics, practice log, and one traceable submitted report were read in 豆包浏览器 without answering or submitting questions; official export history was empty.
- Native one-time, daily, and weekly tasks executed and each read the same Feishu state record.
- Scheduler, partner, cross-device, privacy, and diagnostic surfaces inspected.
- After explicit user confirmation, all three Doubao model-improvement data categories were disabled and read back as closed.
- Capability matrix updated and ADR-001 accepted for the Phase 0 architecture decision.

### Accepted residual limitations

- Native partner configuration and skill rollback/version history are unavailable on the observed account.
- Trusted HTTPS was not deployed because Feishu is the selected cloud state path.
- Feishu calendar client visibility, mobile continuation, and hard platform ceilings remain unproven.
- Scheduled writes remain prohibited until Phase 1 idempotency/retry tests pass.

### Exit criteria

- Complete capability matrix with status, version, identity, steps, evidence, limitations, architecture impact, fallback, and issue IDs.
- Preserve screenshots or logs for every conclusion.
- Obtain a minimal skill sample from the current UI; do not invent platform syntax.
- Record runtime/storage/connector decisions in ADR-001.
- Demonstrate a feasible path for every decision gate in specification section 7.3.

All Phase 0 exit criteria are satisfied with the limitations and fallbacks recorded in `docs/phase-0-closeout.md`.

## Phase 1 — 仓库、数据模型与状态服务

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.3.0

Delivered the canonical schemas, allowlisted state API, immutable raw-event and evidence model, reproducible mastery projection, idempotency/audit rules, backup/export/guarded restore, migration chain, offline replay reference, and 21 fake-data unit tests. A private unshared Feishu Base named `ArchitectPass State v1` was installed with all 15 logical tables. Complete canaries and a mutable profile create/update were independently read back; identical request-ID replays produced no duplicate records.

The native Feishu platform has no table-level append-only constraint, local health checks intentionally have no live Feishu credential, and scheduled writes remain disabled. See `docs/phase-1-closeout.md` for the full evidence and acceptance trace.

### Next activity

Phase 2 starts with a bounded inventory and incremental manifest for only the user-authorized material scopes. No bulk upload or full reprocessing is authorized by Phase 1 completion.
