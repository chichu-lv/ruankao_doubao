# Phase 3 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.5.0
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`
- Acceptance baseline: `04_验收清单.md` section E
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated verification

- Phase 3 Cheko tests: 13/13 PASS.
- Full repository regression: 43/43 PASS.
- `scripts/phase3_healthcheck.py`: JSON contracts, current and historical UI-contract handling, forbidden actions, both sanitized fixtures, post-submission requirement, distinct main-question/answer-item counts, DOM fallbacks, absence of a private network client, and Phase 3 tests PASS.

The custom-paper regression fixture records 20 configured main questions and 21 scored answer items because one stem may contain multiple blanks. It is explicit `workflow_test` data from a user-randomized submission and produces zero practice-attempt, mastery-evidence, mastery-state, wrong-question or review writes, even if item-level metadata is later present.
- Python compile and Git whitespace checks: PASS at closeout.

## Acceptance E trace

| Acceptance item | Result | Evidence |
|---|---|---|
| Task has count, time limit and completion standard | PASS | Required/validated task fields; 15-question/20-minute test |
| Open correct page or give precise manual navigation | PASS | Real `/test_log?subject=0` and `/error_book?subject=0` navigation; versioned routes |
| User answering state is `AWAITING_HUMAN` | PASS | Verified-navigation state transition and real-fixture rehearsal |
| No answer or explanation before submission | PASS | Pre-submit import/content guards and forbidden operation allowlist |
| At least one stable result import | PASS | Real sanitized submitted report `710358` imported as aggregate-only metadata |
| Wrong items recorded | PASS | Item-level K-classified attempt, evidence and review test |
| Low-confidence correct items recorded | PASS | Confidence `0.4` normalized to G and scheduled for review |
| Time and error type recorded | PASS | Item-level duration plus K/G records in immutable practice attempts |
| DOM change switches to fallback | PASS | Edge blank-page observation plus official export/screenshot/manual ordered contract |
| No private API, bulk copy or auto-answer | PASS | No network client; answer/submit operations absent and explicitly blocked |

## Documented limitations

- No new real practice was started or submitted during Phase 3. The stable real import proof uses an already-submitted historical report and intentionally captures aggregate metadata only.
- Real item-level confidence and error classification remain uninitialized. The complete item pipeline is verified with synthetic metadata; the first new user-completed exercise can populate it without code changes.
- Edge displayed a blank content surface for the practice log, while 豆包浏览器 succeeded. Browser automation therefore cannot be the only path.
- The official export entry was visible but not invoked because exporting a potentially broad, sensitive set requires action-time user confirmation.
- Phase 3 did not write the historical result into authoritative Feishu state. It validated the same allowlisted `practice_attempts`/evidence/review contract used by the already-deployed Phase 1 state layer; real history initialization remains Phase 6 work.
