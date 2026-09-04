# Phase 7 accelerated pilot evidence

- Date: 2026-09-04 (Asia/Shanghai)
- Version: 0.8.4
- Mode: isolated seven-logical-day simulation
- Logical interval: 2026-09-04 through 2026-09-10
- Local command: `python3 scripts/phase7_accelerated_pilot.py`
- Local result: `PASS`, 19/19 checks, 0.0306 wall-clock seconds
- Real entry validation: Doubao project `架构上岸教练`, local-computer mode
- Production writes: 0
- External-service calls: 0
- Cheko answers/submissions: 0
- Authoritative learning state: false
- Real seven-day independent pilot satisfied: false
- Repository regression: 85/85 unit tests PASS; Phase 1/4/5 health checks PASS (Phase 1 live-Feishu probe intentionally PARTIAL)

## Exercised paths

1. Seven complete observe-to-checkpoint state-machine sessions and restart recovery.
2. Wrong and low-confidence-correct evidence, reproducible mastery, pending-review deduplication, a three-day-overdue recovery, completion and rescheduling.
3. Targeted video rewatch without restart or mastery inference.
4. Post-submission-only case feedback and essay failure on missing project facts, followed by a synthetic confirmed/redacted fact flow.
5. Choice, case and essay activity plus a weekly report with exactly three priorities.
6. Persistent outbox survival across restart, retention on transport failure, one acknowledged replay, and verified JSON/CSV/Markdown backup exports.
7. No question, option, answer, correct-answer or explanation fields in simulated practice records.

Isolated counts: `sessions=7`, `practice_attempts=4`, `mastery_evidence=4`, `review_queue=2`, `case_attempts=1`, `essay_attempts=1`, `study_events=8`, `audit_log=87`.

## Issues found and fixed

| ID | Observation | Fix | Verification |
|---|---|---|---|
| P7-SIM-001 | Review rows could be scheduled and read but not completed, so completed work could stay pending and block later scheduling. | Added allowlisted `complete_review` with ISO completion time, traceable evidence, audit/idempotency behavior and schema support. | Unit regression plus accelerated overdue completion/reschedule and bounded-queue checks pass. |
| P7-SIM-002 | The first real Doubao run failed at import because the lightweight pilot eagerly required optional `pdfplumber`. | Changed `architectpass_materials` public exports to lazy imports. No package was installed. | A subprocess regression explicitly blocks `pdfplumber`; the real Doubao retry exited 0 and reported PASS. |

## Real Doubao run

The first local-computer run was a truthful environment failure, not a simulation PASS. Doubao identified the exact import chain and did not install dependencies or touch external services. After the repository fix, the same project reran the same script and independently reported:

- `ACCELERATED_PILOT=PASS`
- `logical_days=7`
- all 19 checks true
- `production_writes=0`
- `external_service_calls=0`
- `cheko_answers_or_submissions=0`
- `P7-SIM-001=FIXED_AND_REGRESSION_TESTED`
- `P7-SIM-002=FIXED_AND_REGRESSION_TESTED`
- `real_seven_day_independent_pilot_satisfied=false`

## Acceptance disposition

This run compresses logical time and provides functional, restart and failure-recovery evidence. It cannot prove seven days of real unattended operation, natural scheduled delivery, account-session longevity or service drift. Section K of `04_验收清单.md` therefore remains `DEFERRED / NOT_RUN`; the accelerated result must not be reported as final unconditional acceptance.
