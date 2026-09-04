# Phase 3 sanitized Cheko observation log

- Date: 2026-09-04 (Asia/Shanghai)
- Scope: logged-in real user session, navigation and post-submission metadata only
- Safety rule: no answer selection, submission, restart, close-practice, export, private API call, or bulk question capture

## Browser behavior

- Microsoft Edge retained a logged-in Cheko home page. Direct navigation to `/test_log?subject=0` changed the route, but the content surface remained blank after refresh. This is recorded as a browser-surface failure, not a successful result read.
- The logged-in 豆包浏览器 session loaded the same route normally. The practice log exposed practice type, topic/year, creation time, and semantic buttons such as `继续练习`, `查看报告`, and `查看回顾`.
- A previously submitted ordinary database practice remained reachable through `查看报告`. Its visible report identifier was `710358`; the sanitized captured summary contains only practice type, topic, creation display, 55-question count, score display `42`, and elapsed display `00:19`.
- The report page was already in a post-submission state. Although the UI could display explanations at that point, no question, option, answer, or explanation content was copied into Phase 3 fixtures or evidence.
- `/error_book?subject=0` loaded in 豆包浏览器 and exposed answer-count/date filters, topic rows, progress, `导出PDF`, and `自定义组卷`. No export or practice action was triggered.

## Versioned UI boundary

`deployment/cheko/ui-contract-v1.json` records route plus accessible-role/name locators instead of transient accessibility node numbers. The contract is versioned as `cheko-ui-2026-09-04.1` and defines the ordered fallback:

1. user-triggered official export;
2. post-submission result screenshot;
3. manual result summary containing only result ID, visible item ID, correctness, confidence, error type and time.

The Edge blank-page observation demonstrates why these fallbacks are required. Dynamic node numbers and browser credentials are not stored.

## Real sanitized import rehearsal

The tracked sanitized fixture was passed through the same lifecycle used by the implementation:

```text
CREATED → NAVIGATION_READY → AWAITING_HUMAN → IMPORTED
```

Result:

- pre-import state: `AWAITING_HUMAN`;
- final state: `IMPORTED`;
- detail: `aggregate_only`;
- question count: 55;
- captured item/question bodies: 0;
- four write audits were produced by the reference lifecycle.

The score display is preserved as visible text and is not silently interpreted as a correct-count field. Item-level wrong/low-confidence handling is verified with synthetic metadata tests until the user completes a new practice and supplies confidence/error classifications.

## Explicit non-actions

- Did not click any answer option or submit control.
- Did not start, continue, restart, or close a practice.
- Did not open explanations before submission.
- Did not trigger the official PDF export because its scope could contain sensitive question material.
- Did not inspect network traffic, cookies, local storage, private endpoints, or browser credentials.
- Did not copy any full question bank or question body into the repository.
