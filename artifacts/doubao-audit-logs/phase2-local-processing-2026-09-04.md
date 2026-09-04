# Phase 2 sanitized local-processing evidence

- Date: 2026-09-04 (Asia/Shanghai)
- Authority: the user limited useful Baidu Netdisk material to two named roots and authorized project-scoped access.
- Privacy: private personal exam study; no original course file or transcript was uploaded or committed.
- Access boundary: normal Baidu Netdisk desktop UI and user-authorized local downloads only. No private download API, DRM bypass, CAPTCHA bypass, or hidden URL was used.

## Authorized inventory

The incremental manifest contains only the two user-authorized remote roots. In the first root, the visible lesson directory reported 45 items; 15 visible video rows plus the courseware folder were recorded without bulk download. The second root is retained as an authorized inventory root but was not bulk-enumerated or copied during this bounded Phase 2 proof.

## Real PDF proof

- File: `202605-0.架构导学课.pdf`
- Normal-UI download: complete; 5,803,051 bytes; 10 pages; unencrypted.
- SHA-256: `4a474dd400868889702dcf7105360ba42526161fc72b340935f15d942ad8de2e`.
- Ordinary extraction: unusable for Chinese on all 10 pages, so all were correctly marked OCR candidates.
- Selected OCR: page 8 only. Other pages were not OCR-processed.
- Search probe: `学习方法` returned file `202605-0.架构导学课.pdf`, section `配套学习资料`, page 8, OCR `true`, confidence `0.8849`, a checksum-backed page citation, and a local `#page=8` target.
- Visual QA: all 10 pages were rendered at 72 dpi and individually inspected; no missing page, clipping, or black rendering was observed. The existing synthetic Phase 0 PDF was also rendered and inspected.
- Truthful failure: the first Tesseract TSV invocation produced `OCR_EMPTY` because the isolated tessdata invocation did not enable TSV output as expected. The invocation was corrected to explicitly set `tessedit_create_tsv=1`; the selected-page rerun passed. No failed run was reported as success.

## Real video proof

- File: `202605-0.架构第二版考试介绍考点分析学习方法.mp4`
- Normal-UI download: complete; 197,443,594 bytes; duration 3631.063 seconds; H.264 1920×1080 plus AAC audio.
- SHA-256: `d5d747e7c83c9275538e6c2d60c3d568d1203402f4e8282d35c433f3dd8f0cd7`.
- Player progress readback: `611 / 3631` seconds. It is stored as `played_unchecked`; recall and practice remain false, so playback did not raise mastery.
- Bounded local processing: extracted only `00:10:00–00:11:15` to a mono 16 kHz WAV, then ran local `whisper.cpp` with the pinned Chinese-capable model.
- Transcript result: 39 timestamped segments. Machine transcript confidence is conservatively stored as `0.70` because the SRT has no calibrated per-segment probability and was not manually corrected.
- Search probe: `统一大纲` returned original-video time `643.2–646.6` seconds and fallback target `202605-0.架构第二版考试介绍考点分析学习方法.mp4@00:10:43-00:10:46`. Its citation uses the original video SHA-256, not the derived transcript hash.
- Truthful fallback: sandboxed Metal allocation failed during an earlier GPU probe. CPU mode passed on both a synthetic Mandarin sentence and the real 75-second course clip. The real clip took about 29 seconds on this machine.

## Write and model audit

| Operation | Request ID | Audit ID | Result |
|---|---|---|---|
| Extract real clip | `phase2-real-video-clip-001` | `phase2-real-video-clip-audit-001` | PASS; source/output hashes recorded locally |
| Real local ASR | `phase2-real-video-asr-001` | `phase2-real-video-asr-audit-001` | PASS; model hash and CPU setting recorded locally |
| Video metadata import | `phase2-real-video-import-003` | `phase2-real-video-import-audit-003` | PASS |
| Transcript import | `phase2-real-transcript-import-003` | `phase2-real-transcript-import-audit-003` | PASS |
| Private catalog export | `phase2-real-video-catalog-export-003` | `phase2-real-video-catalog-export-audit-003` | PASS; ignored local output |

Pinned local model hashes:

- `ggml-medium-q5_0.bin`: `19fea4b380c3a618ec4723c3eef2eb785ffba0d0538cf43f8f235e7b3b34220f`
- `chi_sim.traineddata`: `a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730`

Raw downloads, generated audio, transcripts, private indexes, and model binaries remain in ignored local paths. Only schemas, sanitized manifests, code, and this evidence summary are tracked.
