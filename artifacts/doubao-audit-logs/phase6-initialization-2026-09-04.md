# Phase 6 real-data initialization log

- Date: 2026-09-04 (Asia/Shanghai)
- Doubao project: `架构上岸教练`
- State: private Feishu Base `ArchitectPass State v1`
- Conversation evidence: Doubao chat `38440213023143426`
- Result: `COMPLETE_WITH_DOCUMENTED_LIMITATIONS`

## Public-safe initialization plan

Doubao read `deployment/phase6/initialization-write-plan-v1.json` and first performed request-ID lookup, physical-field discovery, canonical-JSON hash verification, and a dry run. It then created and independently read back these 15 records:

| Table | Created | Verified |
|---|---:|---:|
| `user_profile` | 1 | 1 |
| `topics` | 10 | 10 |
| `resources` | 2 | 2 |
| `video_progress` | 1 | 1 |
| `study_events` | 1 | 1 |
| **Total** | **15** | **15** |

Every record used its planned `request_id` and `audit_id`. Fifteen corresponding audit records were created and read back. The profile contains no prior-exam field. The Cheko event is aggregate-only, references already-submitted result `710358`, and carries `mastery_update_allowed=false`; no question, option, answer, or explanation was read or stored.

## Private runtime segments

`scripts/build_phase6_private_segments.py` created the ignored runtime file `dist/phase6-initialization/private-segments-v1.json`. The file explicitly sets `git_commit_allowed=false`. Doubao wrote only its 49 `resource_segments` records into the private Base:

| Segment type | Created | Verified |
|---|---:|---:|
| PDF page anchors | 10 | 10 |
| Video timestamp anchors | 39 | 39 |
| **Total** | **49** | **49** |

All 49 matching audit records were independently read back. Only anchor identifiers were shown in the report; course text was not copied into Git, the chat summary, a public location, or another project.

## Final real-state counts

| Table | Count |
|---|---:|
| `user_profile` | 2 (one Phase 1 canary retained) |
| `topics` | 10 |
| `resources` | 2 |
| `resource_segments` | 49 |
| `video_progress` | 1 |
| `study_events` | 3 (two Phase 1 canaries retained) |
| `audit_log` | 67 (3 prior + 64 Phase 6) |

The other eight tables were independently read as empty: `exam_config`, `study_sessions`, `practice_attempts`, `mastery_evidence`, `mastery_state`, `review_queue`, `case_attempts`, and `essay_attempts`.

An operator prompt mistakenly said “other nine tables”; Doubao enumerated all 15 tables, detected that seven had records and therefore only eight were empty, and reported the mismatch instead of accepting the expected count.

## Idempotency replay

A separate read-only replay checked all 64 Phase 6 request IDs (15 public-safe initialization records plus 49 private segments). Result: `64/64 DEDUP_VERIFIED`, `0 FAIL`, `0 supplemental writes`. Before/after table counts were identical. Each business record and audit record matched its primary key, canonical payload hash, payload, request ID, and audit ID.

## Deliberately uninitialized data

- Prior exam attempts and scores: optional; neither requested nor inferred.
- Project facts: versioned empty store with `awaiting_user_confirmed_redacted_facts`; no facts invented.
- Mastery: no level inferred from playback, index text, or aggregate Cheko results.
- Official exam configuration and syllabus weights: pending official-source verification.
- First study-session checkpoint: created only after the user starts and completes the first real training session.
- Production schedule times: still pending user preference; no task was changed.

No existing project, permission, schedule, `pass_ai` file, or unrelated Feishu record was modified.
