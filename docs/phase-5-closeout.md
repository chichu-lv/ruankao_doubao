# Phase 5 closeout — private Doubao deployment

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.7.1

Phase 5 packages the product into nine single-responsibility, versioned private Doubao skills using the real client-observed `SKILL.md` format. Deterministic archives use one same-name top-level directory, are secret-scanned during build, and have SHA-256 values in an ignored build manifest. The deployment manifest forbids arbitrary SQL, shell and filesystem access; Cheko answer/submit and pre-submission content; private API reverse engineering; public publishing; unconfirmed deletion, permission changes, and sensitive export.

The final delivery entry is the Git repository rather than the developer machine's installed state. The root README contains one short prompt accepting a user-supplied private repository URL; `deployment/doubao/bootstrap-v1.md` defines the evidence-gated fetch, verify, build, private-project creation, skill installation, baseline attachment, state connection, read-only scheduling, health-check and reporting flow.

All nine formal skills were installed in the user's real Doubao 2.27.11 account, registered READY, enabled, and visible from the project composer. The scheduler skill completed the platform safety scan before being treated as enabled. A new isolated private Project named `架构上岸教练` was created so the existing `系统架构设计师 AI Tutor` / `pass_ai` project remained untouched.

The new project's initialization chat read the rendered production system instructions plus both deployment manifests from exact allowlisted repository paths and adopted the instructions as its current control baseline. Its real read-only health check was `PARTIAL`; the detailed seven-row matrix was `PASS × 5`, `PARTIAL × 2`, `FAIL × 0`. Skills, Feishu state, local citations, Browser/Baidu fallback, and existing read-only schedule access were feasible; Cheko login was intentionally not re-probed, and no first learning checkpoint exists yet. The generated report headline incorrectly said four PASS, so the evidence log preserves that reporting mismatch.

The connector configuration continues to use built-in Feishu tools and the private `ArchitectPass State v1` Base as authoritative state. The daily and weekly production prompts are read-only, reference that same state source, and have zero write operations. Activation is intentionally pending the user's preferred execution times; existing Phase 0 read-only schedules were inspected but not changed.

This satisfies the Phase 5 delivery set: skill packages, connector/project manifests, private equivalent project container, rendered system instructions, read-only schedule templates, minimum permissions, and installation/update/rollback guidance. Evidence and acceptance details are in `artifacts/doubao-audit-logs/phase5-installation-2026-09-04.md` and `docs/test-results/phase-5.md`.

## Documented limitations

- The current account exposes no separate private custom-partner editor or persistent project-level system-instruction field. The isolated private Project plus its initialization context is the verified equivalent path.
- Exact local-folder attachment is not proven: the macOS picker did not preserve the exact child selection through automation. No parent directory was saved; exact allowlisted paths worked in local-computer mode.
- Cheko login/routes were not opened during the Phase 5 health check. Phase 3 evidence and the export/screenshot/manual fallback remain valid, but login must be checked before the next real practice.
- No learning checkpoint exists before Phase 6 real-data initialization. No write was fabricated to close this gap.
- Production daily/weekly task names and user-preferred times are not activated. Existing Phase 0 read-only jobs continue unchanged, and scheduled writes remain disabled.
- The Git-driven bootstrap contract is implemented and statically tested, but a second clean-room installation from the final remote URL cannot be verified until that URL exists. The current real-account installation remains the functional reference evidence.
- Rollback is disable/re-enable by version because the observed platform exposes no reliable version history. Deletion always requires a fresh explicit confirmation.

## Next gate

Phase 6 may initialize the authorized material/video state, the first knowledge-map state, a post-submission Cheko baseline, redacted project facts, and an initial seven-day plan. Prior exam attempts and scores are optional and must not be requested as an entry condition; if the user voluntarily supplies them, only confirmed values may be stored. Every write requires an idempotency request ID, audit ID, and read-back verification.
