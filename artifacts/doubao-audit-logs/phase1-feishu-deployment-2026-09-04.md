# Phase 1 Feishu deployment log

- Executed in: real Doubao desktop account, cloud-computer task, Feishu connector only
- Date: 2026-09-04 (Asia/Shanghai)
- Object: private, unshared `ArchitectPass State v1`
- Stable base ID: `EyjxbTJUtafqe3sA7mRchccXnAh`
- Deployment request/audit: `req-phase1-schema-001` / `audit-phase1-schema-001`
- Scheduled writes: not created or enabled

## Structure result

All 15 tables in `deployment/feishu/production-v1.json` were created and independently listed. Ordinary tables have primary key plus `request_id`, `audit_id`, `actor`, `created_at`, `payload_json`, and `content_sha256`. `audit_log` has six fields because its `audit_id` primary key already fulfills the common audit-ID role. `mastery_state` additionally has `derived_rule_version` and `evidence_ids_json`.

Feishu Bitable did not expose a native table-level append-only constraint. The deployment did not claim otherwise. Append-only behavior remains an application/write-protocol invariant.

## Truthful correction of incomplete first canary

The first two canary records were successfully created but read back with empty `created_at` and `content_sha256`. They were not modified or deleted. Instead, two complete superseding records were appended:

| Table | Stable record ID | Primary ID | Request ID | Created at | SHA-256 |
|---|---|---|---|---|---|
| `audit_log` | `recvudIQKnwFrw` | `audit-phase1-bootstrap-002` | `req-phase1-bootstrap-002` | `2026-09-04T11:55:00.000+08:00` | `1c6750e442f80718068e9bae0defe8ea60fe77c9e1d811b76d7f5ea7230dd724` |
| `study_events` | `recvudIRnoXXcW` | `phase1-canary-002` | `req-phase1-canary-002` | `2026-09-04T11:55:01.000+08:00` | `5e5cb9bf4ab22bb56463efe5142ad6d2bd2095fdffb8131cee11aed683bb359f` |

The study-event source anchor is `resource_id=phase1-spec, pdf_page=1`; it supersedes `phase1-canary-001` without overwriting that fact.

## Idempotency replay

The foreground workflow implemented `query request_id -> create only if absent -> read back`. First lookup returned zero records for each complete canary and created the stable IDs above. Immediate replay of each identical request returned exactly one existing record and did not add another. Final independent read returned the requested field values and exact SHA-256 strings.

This proves the bounded workflow protocol, not a native Feishu uniqueness constraint. All production writers must continue using this protocol; scheduled writes remain disabled pending scheduled-retry characterization.

## Mutable profile read/write test

A harmless `phase1-test-user` profile was created, independently read, updated from 60 to 90 weekday minutes, and read again. Stable profile record ID: `recvudK4T5mXHC`. The update used `req-phase1-profile-update-001` and read back SHA-256 `43539ddfe21e6b9752a0fa67caedec02c296797fc479c3f3286a8e8845ef76a0` while preserving `user_id`, `actor`, and `created_at`.

Audit record `recvudK6xSWgdw` / `audit-phase1-profile-update-001` was appended with before hash `c1031b09be1bca9cee134ea5bfa1b646a162482bac2080c2b87225b88204c8af`, the after hash above, success status, and rollback reference `phase1-profile-create-001`. It was independently read back. No unrelated record was touched.
