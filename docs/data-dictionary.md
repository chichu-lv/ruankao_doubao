# Phase 1 data dictionary

All production tables are private Feishu Bitable tables. Every written record also carries `request_id`, `audit_id`, `actor`, and timestamps at the adapter boundary. JSON-shaped fields are stored as canonical JSON text if the current Bitable field type cannot represent them natively.

| Table | Primary key | Role | Mutation rule |
|---|---|---|---|
| `user_profile` | `user_id` | Exam target, time budget, preferences and constraints | patch through allowlist |
| `exam_config` | `exam_name` | Versioned exam rules and official sources | source and `verified_at` required |
| `topics` | `topic_id` | Hierarchical syllabus topic graph | versioned, source-referenced |
| `resources` | `resource_id` | Metadata only for PDF/video/web/Cheko/note | no original course body |
| `resource_segments` | `segment_id` | Page/time segments and citation anchors | incremental, checksum-aware |
| `video_progress` | `video_id` | Watched position and capability conversion status | state enum, no playback=mastery shortcut |
| `study_sessions` | `session_id` | Session lifecycle and checkpoint | every finished session has full checkpoint |
| `practice_attempts` | `attempt_id` | Submitted-result evidence and confidence | append; no pre-submit answer content |
| `study_events` | `event_id` | Raw learning facts | immutable append-only |
| `mastery_evidence` | `evidence_id` | Scored, typed evidence | immutable append-only |
| `mastery_state` | `topic_id` | Recomputable 0–5 projection | derived only |
| `review_queue` | `review_id` | Due work | one pending topic+type pair |
| `case_attempts` | `case_id` | User answer and rubric coverage | append revisions as new facts |
| `essay_attempts` | `essay_id` | Outline/full essay tied to real project facts | append revisions; no invented facts |
| `audit_log` | `audit_id` | Who/what/before-after hashes/result/confirmation/rollback | immutable append-only |

## Raw study event

`event_id`, `event_type`, `topic_ids`, `session_id`, `payload`, `source_ref`, and `occurred_at`. `source_ref` must contain a traceable anchor and never stores credentials or a full copyrighted question.

## Mastery evidence and projection

Evidence types are ordered but retain their raw scores: viewed, open-book recall, closed-book recall, untimed choice, timed choice, case points, essay application and timed mock. Their maximum levels are respectively 1, 1, 2, 3, 3, 4, 5 and 5. A score below 0.6 does not establish that level, and level 3 requires at least two reliable choice-result records so one accidental correct answer cannot establish mastery. Low confidence remains a risk even when the answer is correct. The projection records evidence IDs and `mastery-v1`, so it can always be reproduced.

## Checkpoint

A finished session checkpoint must include `completed`, `incomplete`, `discoveries`, `mastery_changes`, `next_due`, `resume_context`, and `write_status`. `AWAITING_HUMAN` is a valid live state for browser exercises and is not failure.

## Stable error codes

`INVALID_WRITE_CONTEXT`, `VALIDATION_ERROR`, `UNTRACEABLE_SOURCE`, `FIELD_NOT_ALLOWED`, `OPERATION_NOT_ALLOWED`, `IDEMPOTENCY_CONFLICT`, `AUDIT_ID_CONFLICT`, `IMMUTABLE_RECORD`, `INCOMPLETE_CHECKPOINT`, `CONFIRMATION_AND_BACKUP_REQUIRED`, `NOT_FOUND`, `PATH_NOT_ALLOWED`, `UNSUPPORTED_SCHEMA_VERSION`, `BACKUP_CHECKSUM_MISMATCH`, and `STALE_PRE_RESTORE_BACKUP`.
