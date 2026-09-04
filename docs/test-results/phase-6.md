# Phase 6 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.8.0
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`, Phase 6 and section 11
- Acceptance baseline: `04_验收清单.md`, sections C, D, E, F, G and I
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated checks

- Initialization-unit tests cover optional exam history, exact authorized evidence, unique request/audit IDs, no mastery inference, provisional sourced topics, a bounded seven-day plan, an explicitly empty project-fact store, deterministic rendering, and private PDF/video anchors.
- `scripts/phase6_healthcheck.py` renders the public-safe plan, builds or truthfully defers the ignored private-segment plan, verifies policy, and runs the Phase 6 tests.
- Full repository regression and Git whitespace checks are recorded after the final closeout run.

## Real-account checks

| Check | Result | Evidence |
|---|---|---|
| Profile without exam history | PASS | Created and read back; no `past_exam_scores` field. |
| Provisional knowledge map | PASS WITH LIMITATION | Ten sourced nodes created; weights remain null pending official verification. |
| First resource metadata | PASS | One PDF and one video record created and verified. |
| Video progress | PASS | `611/3631`, `played_unchecked`, no mastery conversion. |
| PDF page index | PASS | 10/10 private page segments verified with `#page=` anchors. |
| Video timestamp index | PASS | 39/39 private segments verified with original `#t=` anchors. |
| Submitted Cheko baseline | PASS WITH LIMITATION | Aggregate event `710358` stored post-submission; no item evidence or mastery update. |
| Project facts v1 | PARTIAL | Versioned empty fact store; waits for voluntary confirmed/redacted facts and forbids fabrication. |
| Seven-day plan | PASS WITH LIMITATION | Seven-day three-subject rotation bounded by runtime fractions; minute values wait for daily availability. |
| Idempotent replay | PASS | 64/64 DEDUP_VERIFIED; zero new records and unchanged counts. |
| Unauthorized table writes | PASS | Eight untouched tables remained empty; existing Phase 1 canaries were preserved. |

## Final run

- `python3 scripts/phase6_healthcheck.py`: PASS, including 10/10 Phase 6 initialization tests, public/private allowlisted API replay, and the 49-segment private runtime plan.
- Full repository unit suite under the bundled Python 3.12 runtime: 75/75 PASS.
- `git diff --check`: PASS at closeout.
