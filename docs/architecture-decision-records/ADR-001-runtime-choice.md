# ADR-001: Phase 0 runtime, persistence, and integration choice

- Status: PROVISIONAL - Phase 0 gates are not all closed
- Date: 2026-09-04
- Decision owners: Codex + user

## Context

The product baseline requires Doubao to remain the sole user-facing controller. Architecture must follow the capabilities observed in the user's real account and computer, not promotional assumptions. The audit demonstrated a private custom skill, authorized local PDF reading, named Baidu course access, Feishu account writes, and visible 芝士架构 progress. It did not yet demonstrate a native private custom partner, Doubao-to-Feishu state access, a working connector endpoint, or executed scheduled tasks.

## Decision

1. Use the installed Doubao desktop client as the primary controller.
2. Use the private Doubao Project `系统架构设计师 AI Tutor` as the persistent configuration entry because the current standard-plan UI did not expose private custom-partner creation.
3. Package bounded workflow behavior as private skills derived from the captured real `SKILL.md` format.
4. Accept explicit local-file attachment and the two user-designated Baidu Netdisk course scopes as Phase 0 material-retrieval paths.
5. Treat Feishu multidimensional tables as the preferred candidate structured state layer only after Doubao can read and write the same test object. If that path fails, implement a trusted HTTPS state service with allowlisted operations, idempotency request IDs, audit IDs, and server-side secret storage.
6. Do not select localhost as the authoritative state path until DB-012 is re-tested outside the current port-binding restriction and native schedules are shown to reach it.
7. Use screenshot/manual visible-result import as the minimum safe 芝士架构 integration. Do not automate answers, expose answers before submission, scrape private APIs, or copy the full question bank.
8. Keep the native Doubao scheduler as the preferred reminder path, but do not enter Phase 1 until one-time/daily/weekly tests prove execution and identify whether scheduled work can access the chosen state layer.

## Consequences

- Doubao remains the only conversational controller.
- Current work can continue on Phase 0 artifacts and bounded probes, but large-scale implementation is blocked.
- The lack of a native custom partner is handled by an equivalent private Project rather than by replacing Doubao.
- Authoritative learning state will not live only in chat history or local SQLite.
- All platform gaps retain manual, screenshot, or restricted-service fallbacks.

## Evidence

- `docs/doubao-capability-matrix.md`
- `artifacts/doubao-audit-logs/phase0-observations-2026-09-04.md`
- `artifacts/doubao-skill-samples/phase0-capability-probe/`
- `artifacts/doubao-audit-screenshots/`
- `output/pdf/phase0-local-file-probe.pdf`

## Remaining gate tests

- Prove Doubao access to the same Feishu state object or pass a trusted HTTPS connector test.
- Execute one-time, daily, and weekly schedules and observe retry/history behavior.
- Complete a post-submission 芝士架构 result-page or official-export import test without answering questions.
- Record the user's privacy-setting choice before any sensitive material is transmitted.
