# Phase 3 closeout — safe Cheko practice adaptation

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.5.0

Phase 3 delivers a safety-first Cheko practice lifecycle controlled by Doubao. Tasks require subject, mode, target, question count, time limit, completion standard, confidence capture and an allowlisted navigation route. A task reaches `AWAITING_HUMAN` only after the expected route is verified; the user remains responsible for answering and submitting.

Result import accepts only post-submission visible reports, official exports, screenshots or manual summaries. Every input level uses an explicit field allowlist. Question bodies, options, answers, correct answers, explanations, raw HTML and unknown payload fields are rejected. There is no HTTP/private-API client and no answer/submit operation.

Item-level submitted metadata becomes immutable `practice_attempts` plus reproducible mastery evidence. Wrong items require K/C/M/A/Q/T/E classification. Correct items below confidence `0.6` are normalized to G and enter the review queue; reliable correct items do not create a review solely for being correct.

Real UI validation succeeded in 豆包浏览器 for practice logs, one historical submitted-report entry and the error-book page. Edge's blank result demonstrates the need for the versioned official-export → screenshot → manual-summary fallback. The historical summary imported without copying any question content.

All ten section-E acceptance checks have an evidence-backed path. See `docs/test-results/phase-3.md` and the sanitized observation log for limitations.
