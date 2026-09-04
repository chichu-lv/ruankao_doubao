# Phase 2 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.4.0
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`
- Acceptance baseline: `04_验收清单.md` section D
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated verification

- Phase 2 material tests: 12/12 PASS.
- Full repository regression: 33/33 PASS.
- `scripts/phase2_healthcheck.py`: all five binaries, both local model hashes, authorized-root constraints, write context, progress policy, no-mastery-from-viewing rule, and Phase 2 tests PASS.
- `compileall`: PASS.
- `git diff --check`: PASS at closeout.

The material suite covers page extraction, search and anchors, hash deduplication, request replay, conflict-safe catalog export, path allowlisting, quarantine receipts, subtitle timestamps, clip-to-original time offsets, real ffmpeg extraction behavior, fixed non-shell Whisper arguments, derived-file audit receipts, and diagnosis-before-targeted-rewatch behavior.

## Acceptance D trace

| Acceptance item | Result | Evidence |
|---|---|---|
| PDF incremental import and hash dedupe | PASS | SHA-256 resource IDs plus duplicate/replay tests |
| PDF search returns file, section and page | PASS | Real page-8 query returned all fields and local page target |
| OCR only when necessary and local | PASS | All pages detected as candidates; only explicitly selected page 8 OCR-processed |
| Video audio and timestamped subtitles | PASS | Real 75-second clip produced 39 SRT segments locally |
| Video search returns file and time range | PASS | Real query returned `643.2–646.6` seconds |
| Open or clearly identify target | PASS | PDF `#page=8`; video filename plus `00:10:43–00:10:46` fallback |
| Half-watched progress imported | PASS with low-confidence scope | Course-level `0.5` user statement plus observed first-video `611/3631` seconds |
| Watched content uses diagnosis then targeted rewatch | PASS | `played_unchecked` state and planner test prohibit restart/mastery mutation |
| Original course files not publicly uploaded | PASS | Raw, parsed, index and model paths are git-ignored; no upload performed |
| Parse failure has quarantine/manual fallback | PASS | Invalid-PDF receipt retains source; filename/page/time manual targets remain usable |

Detailed sanitized real-file evidence is in `artifacts/doubao-audit-logs/phase2-local-processing-2026-09-04.md`.

## Documented limitations

- Phase 2 proves the pipeline on one real 10-page PDF and one bounded 75-second range of one real video. It does not claim that all 45 visible lesson items or the second authorized root are fully indexed; bulk initial content processing belongs to Phase 6 and should remain incremental.
- Automatic seek from an index result is not treated as stable. The accepted fallback is exact filename plus timestamp; the user can continue watching in Baidu Netdisk without being blocked.
- The real machine transcript is not human-corrected and is marked confidence `0.70` rather than `1.0`.
- GPU acceleration failed in the sandbox; CPU transcription is the verified local path.
