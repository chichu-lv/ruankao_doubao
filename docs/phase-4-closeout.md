# Phase 4 closeout — learning decision engine

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.6.0

Phase 4 composes the existing state, materials and Cheko boundaries into the fixed `OBSERVE → DIAGNOSE → PLAN → EXECUTE → TEST → UPDATE → SCHEDULE → CHECKPOINT` lifecycle. A session cannot be planned before a timestamped observation containing the profile, exam date, due reviews, 7/14/30-day score windows, video progress, all three subject ratios and prior incomplete work. Each transition is allowlisted, request-ID idempotent and audit-ID traceable. `AWAITING_HUMAN` is a valid execution state and only a traceable user-output reference can move it to testing.

Plans never exceed the user's time budget. Every item contains a duration, action and completion standard, and 5–10 minutes are reserved for review/state/checkpoint work. Priority preserves the specified six normalized factors, records the exact base score, and exposes separate subject-balance and energy-fit adjustments. A subject below 15% over 14 days or untouched for seven days is boosted; low energy reduces high-load priority while retaining a viable study plan.

Mastery remains the Phase 1 evidence-derived 0–5 projection. Viewing cannot exceed level 1, level 3 needs repeated reliable choice evidence, and K/C/M/A/Q/T/E/G remain enforced. The review scheduler starts from 1/3/7/14/30 days, advances weak/low-confidence/severe/high-importance items, delays stable evidence, explains its signals and removes dates after the exam.

Case coaching is post-submission only and returns intent, covered points, missing points, irrelevant/redundant content, expression flags, concise-rewrite guidance, source references and transfer practice. Essay coaching only accepts confirmed, redacted project facts across the specification's complete fact categories. Missing facts produce a gap report with `fabrication_allowed: false`; unknown fact IDs fail closed. The workflow covers topic, fact matching, outline, partial paragraph, timed full text, grading, revision and spaced rewrite, while preserving time, word count, version and five scoring dimensions.

Weekly reporting returns all three subject ratios, plan/review completion, rising/falling topics, error frequencies, timed-mock trend, case gaps, essay coverage, exactly three next priorities, low-value behaviors to stop and an explicit adjustment basis. Sprint mode uses exam date plus remaining syllabus fraction (`14 + 21 × remaining_fraction`) rather than a fixed calendar day.

All section F and G checks have an implementation and automated evidence path. See `docs/test-results/phase-4.md`.

## Documented limitations

- The Phase 4 engine is provider-independent local code. Phase 5 must package and install its responsibilities as private Doubao skills and connect them to the already-private Feishu state.
- No real company project facts were requested or stored in this phase. Phase 6 must initialize only user-confirmed, redacted facts; missing categories remain explicit.
- Case rubric matching is deterministic reference logic, not a substitute for the final model-based private skill. It requires sourced rubric points and never operates before user submission.
- The weekly report generator is tested with synthetic state. A native scheduled weekly read against the same real Feishu state remains a Phase 5 installation check.
- Sprint mode changes the plan policy but cannot establish exam readiness without real timed-mock, case and essay evidence.
