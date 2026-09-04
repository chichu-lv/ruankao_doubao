# Phase 4 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.6.0
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`, Phase 4 and sections 9–11
- Acceptance baseline: `04_验收清单.md`, sections F and G
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated verification

- Phase 4 controller/state tests: 26/26 PASS.
- Phase 4-specific tests: 14/14 PASS.
- Full repository regression: 57/57 PASS.
- `scripts/phase4_healthcheck.py`: contracts, fixed state order, review baseline, answer/submit absence, anti-fabrication guard and tests PASS.
- Python compile and Git whitespace checks: PASS at closeout.

## Acceptance F trace

| Acceptance item | Result | Evidence |
|---|---|---|
| Read state before every start | PASS | `start_session` requires complete timestamped observation; planner rejects missing observation |
| Plan does not exceed available time | PASS | bounded-selection test and 5–10 minute reserve |
| Every item has duration/action/completion | PASS | candidate validation and plan assertion |
| Due reviews and high-risk topics prioritized | PASS | exact factor formula and retained priority explanation |
| Three subjects not long neglected | PASS | 14-day ratio/seven-day subject-balance boost test |
| Video completion does not mean mastery | PASS | `mastery-v1` viewed ceiling plus existing regression |
| Evidence-based mastery 0–5 | PASS | typed ceilings, repetition rule and evidence IDs in derivation |
| K/C/M/A/Q/T/E/G usable | PASS | diagnosis mapping plus practice validation/G normalization regressions |
| Low energy produces reduced-load plan | PASS | high-load penalty and nonempty reduced plan test |
| Near exam switches to sprint | PASS | exam-date/progress-derived threshold test |

## Acceptance G trace

| Acceptance item | Result | Evidence |
|---|---|---|
| User answers case first | PASS | `submitted_by_user` plus nonempty answer gate |
| Covered/missing/redundant/expression feedback | PASS | post-submit case feedback test |
| Case conclusions have sources | PASS | rubric rejects any point without `source_ref` |
| Real project fact base | PASS | validated fact categories with confirmation and redaction requirements |
| Missing facts reported, never invented | PASS | incomplete fact-base test returns missing categories and forbids fabrication |
| Topic→facts→outline→full→revision | PASS | expanded eight-step workflow assertion |
| Time/word count/version/scoring dimensions | PASS | essay submission test with five normalized dimensions |
| Weekly report detects case/essay underinvestment | PASS | 10%/10% synthetic allocation test flags both |

## Test-data boundary

All Phase 4 tests use synthetic topics, scores, answers and project facts. No real company-confidential facts, Cheko question bodies, answers, credentials or account tokens are present.
