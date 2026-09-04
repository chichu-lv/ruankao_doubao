# ADR-001: Phase 0 runtime, persistence, and integration choice

- Status: ACCEPTED FOR PHASE 0 - residual capability checks remain
- Date: 2026-09-04
- Decision owners: Codex + user

## Context

The product baseline requires Doubao to remain the sole user-facing controller. Architecture must follow the capabilities observed in the user's real account and computer, not promotional assumptions. The audit demonstrated a private custom skill, authorized local PDF reading, named Baidu course access, visible 芝士架构 progress, and a private Feishu multidimensional table created, written, and read by Doubao. Native one-time, daily, and weekly tasks then read that same record. A private custom MCP connector also completed a localhost round trip in local-computer mode. The current account still does not expose native private custom-partner creation.

## Decision

1. Use the installed Doubao desktop client as the primary controller.
2. Use the private Doubao Project `系统架构设计师 AI Tutor` as the persistent configuration entry because the current standard-plan UI did not expose private custom-partner creation.
3. Package bounded workflow behavior as private skills derived from the captured real `SKILL.md` format.
4. Accept explicit local-file attachment and the two user-designated Baidu Netdisk course scopes as Phase 0 material-retrieval paths.
5. Select private Feishu multidimensional tables as the Phase 1 structured state layer because foreground Doubao and native scheduled tasks successfully accessed the same test object. Every write must carry an idempotency request ID and audit ID, use read-after-write verification, and preserve raw learning events. Retain a trusted HTTPS state service with allowlisted operations as a fallback if table constraints appear during implementation.
6. Do not select localhost as the authoritative state path. DB-012 passed only in `工作任务·本地电脑`; the same connector was unavailable in `云电脑`, and scheduled reachability is unproven. Use it only for bounded foreground local operations with a manual fallback.
7. Use screenshot/manual visible-result import as the minimum safe 芝士架构 integration. Do not automate answers, expose answers before submission, scrape private APIs, or copy the full question bank.
8. Use the native Doubao scheduler as the preferred reminder path. One-time, daily, and weekly modes all executed and read the chosen Feishu state layer. Scheduled writes remain disallowed until write deduplication and retry behavior are implemented and tested.

## Consequences

- Doubao remains the only conversational controller.
- Section 7.3 decision gates have evidence-backed paths, but Phase 0 closeout still requires the residual audit checks and the user's privacy decision.
- The lack of a native custom partner is handled by an equivalent private Project rather than by replacing Doubao.
- Authoritative learning state will not live only in chat history or local SQLite.
- All platform gaps retain manual, screenshot, or restricted-service fallbacks.

## Evidence

- `docs/doubao-capability-matrix.md`
- `artifacts/doubao-audit-logs/phase0-observations-2026-09-04.md`
- `artifacts/doubao-skill-samples/phase0-capability-probe/`
- `artifacts/doubao-audit-screenshots/`
- `output/pdf/phase0-local-file-probe.pdf`

## Remaining Phase 0 checks

- Characterize scheduled failure/retry behavior and enforce write deduplication during implementation.
- Complete a post-submission 芝士架构 result-page or official-export import test without answering questions.
- Record the user's privacy-setting choice before any sensitive material is transmitted.
- Close the remaining skill update/rollback/remove, trusted-HTTPS/authentication, Feishu calendar, file-limit, and cross-device audit rows or record their final constrained fallbacks.
