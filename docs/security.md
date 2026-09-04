# Security and privacy

- State, skills, evidence and backups are private by default.
- Secrets are accepted only from the platform's secure connection storage or environment variables and are never logged.
- The logical API is an explicit allowlist; arbitrary SQL, shell, filesystem and private API access are absent.
- Writes require non-empty `request_id`, `audit_id` and `actor`. Audit records store hashes instead of full before/after sensitive bodies.
- Original learning events and mastery evidence are immutable. Deletion of mutable state requires an explicit user confirmation and a pre-existing backup reference.
- Backup targets are restricted to one configured directory and plain `.json` filenames. Exporting real sensitive data remains a confirm-at-action operation.
- Cheko integration may import visible submitted-result identifiers and aggregate facts only. It never answers, submits, reads answers before submission, scrapes private APIs or copies the full question bank.
- Course files remain local or in the two user-authorized Baidu Netdisk scopes and are not uploaded to the state layer.
- Doubao model-improvement sharing for text, files and audio was disabled during Phase 0 and verified in the real UI.

## Threat-focused controls

| Threat | Control |
|---|---|
| Duplicate transport retry | request-ID fingerprint and stable first result |
| Request ID reused for another payload | `IDEMPOTENCY_CONFLICT`, no mutation |
| AI-inferred mastery | only typed raw evidence can drive `mastery-v1` |
| Lost or tampered backup | canonical SHA-256 manifest verified before restore |
| Path traversal | allowlisted directory plus plain filename validation |
| Silent offline loss | failed response remains failed; outbox retains item until acknowledged |
| Destructive mistake | confirmation + backup reference + audit rollback pointer |
| Copyrighted course leakage | raw/downloaded/parsed/index paths ignored; no public or cloud upload |
| Path escape during import | real-path resolution against explicit authorized roots |
| Derived-file overwrite | request fingerprint plus adjacent audit receipt; conflicts fail closed |
| Overconfident ASR | machine transcript confidence explicitly bounded and marked unreviewed |
| Private API/DRM bypass | normal Baidu UI/local files only; filename+timestamp fallback |

## Phase 2 data boundary

Local model binaries, course PDFs/videos, extracted audio, transcripts and private indexes are excluded from Git. The tracked material manifest contains filenames, sizes, checksums, bounded indexed ranges and source anchors but no account token, cookie, private download URL or device identifier. Search is designed to return only a bounded snippet with a page/time citation. Cheko content is outside this pipeline and no question or answer content was imported.

## Phase 3 Cheko boundary

| Threat | Control |
|---|---|
| Automated answering/submission | operations do not exist in the allowlist; user remains `AWAITING_HUMAN` |
| Pre-submit answer leakage | submitted-state gate plus recursive forbidden-content keys |
| Whole-page/question-bank capture | exact field allowlists reject raw HTML, question text, options and unknown fields |
| Private API reverse engineering | no HTTP client; visible UI and user-provided artifacts only |
| DOM drift | versioned route/semantic contract with official export, screenshot and manual fallback |
| Lost weak-signal evidence | wrong items and G-classified low-confidence correct items both schedule review |

The real Phase 3 fixture stores only an already-visible submitted result ID and aggregate display metadata. It contains no question, option, answer, explanation, cookie, account credential or private endpoint.

## Phase 4 decision and coaching boundary

| Threat | Control |
|---|---|
| Plan produced from stale/absent state | complete timestamped observation required before diagnosis or plan |
| Plan overruns the user's time | positive item durations, bounded selection and reserved checkpoint time |
| Subject neglect | explicit 14-day ratio and days-since-subject balance signal |
| Case answer leakage | grading requires `submitted_by_user`; controller has no answer/submit action |
| Standard answer overwrites user reasoning | feedback preserves covered/missing/redundant/expression dimensions and gives guidance rather than replacement |
| Fabricated company facts | confirmed and redacted fact IDs only; missing/unknown facts fail closed |
| Fixed or hidden sprint behavior | threshold derived from exam date and remaining syllabus fraction and emitted with its rule |
| Untraceable review priority | normalized factors, adjustments, schedule signals and reasons are returned in every derived result |
