# Phase 6 closeout — real-data initialization

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.8.0

Phase 6 now has a deterministic, Git-delivered initialization layer plus verified writes in the user's real private state. The public-safe plan initializes a profile without exam history, a ten-node provisional three-subject knowledge map, two authorized resource records, the observed `611/3631`-second `played_unchecked` video position, and an aggregate-only submitted Cheko baseline that cannot update mastery.

The private runtime segment builder consumes only the two exact Phase 2 catalog paths and writes its output under ignored `dist/`. Ten PDF page anchors and 39 original-video timestamp anchors were written to the private Feishu Base without committing course text. Across both batches, 64 business records and 64 audit records were independently read back with matching primary keys, canonical payload hashes, payloads, request IDs, and audit IDs.

A second read-only replay returned `64/64 DEDUP_VERIFIED`, created no record, and left all counts unchanged. The final real state contains 10 topics, 2 resources, 49 segments, 1 video-progress record, one Phase 6 aggregate event and 64 Phase 6 audits. Existing Phase 1 canaries were preserved.

The initial seven-day plan is versioned as a runtime-budgeted three-subject rotation. Each day allocates 90% of whatever time the user provides and reserves 10% for checkpoint work, so no guessed personal schedule is required. Historical exam participation and scores are neither requested nor inferred.

See `artifacts/doubao-audit-logs/phase6-initialization-2026-09-04.md` and `docs/test-results/phase-6.md`.

## Documented limitations

- The knowledge map is provisional: source references are traceable, but official syllabus weights remain `null` until an official source is reachable and verified.
- Project-facts v1 is deliberately empty. It blocks factual essay drafting until the user voluntarily supplies confirmed, redacted facts; structure-only drills may continue.
- `exam_config` remains empty because the official web query did not return during this run. No date or rule was hardcoded.
- The seven-day plan is budgeted by fractions and becomes a minute-level plan only when the user starts each day with available minutes and energy.
- No study-session checkpoint exists yet; initialization is not falsely recorded as completed learning. The first real session must finish with a checkpoint.
- Production schedule names/times remain pending user preference, and scheduled writes remain disabled.

## Next gate

Phase 7 must run the specification's end-to-end, failure/recovery, safety and same-state schedule cases on the real Doubao project. The seven-day independent pilot remains a separate final acceptance gate.
