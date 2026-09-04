# Phase 2 closeout — material ingestion and traceable retrieval

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.4.0

Phase 2 now has a bounded, private and reproducible local material pipeline. It discovers only authorized inputs, hashes and deduplicates resources, extracts PDF pages, performs selected-page Chinese OCR, probes video, extracts bounded audio, generates local timestamped Chinese SRT, preserves clip offsets against the original video, searches without returning whole source bodies, and emits source-backed page/time targets.

Every persisted material import, derived audio/transcript, manifest and catalog export carries a request/audit context. Derived-file replays are idempotent and conflicts do not overwrite prior output. Invalid PDFs produce a receipt without moving or deleting the source.

The real acceptance probe used one downloaded course PDF and one course video from the user-authorized Baidu Netdisk scope. Raw/private material, model binaries, generated transcripts and indexes stay local and ignored. The tracked repository contains only code, schemas, sanitized manifests and evidence summaries.

The imported course progress remains approximate (`0.5`, user statement, low confidence), with one player observation at `611/3631` seconds. Its status is `played_unchecked`: the next action is a diagnostic over the watched portion. Only evidence-backed weak ranges may become targeted rewatch ranges; neither playback nor rewatch changes mastery by itself.

All ten checks in acceptance section D have evidence-backed paths. See `docs/test-results/phase-2.md` for the trace and limitations. Phase 3 may begin without bulk-indexing the rest of the course.
