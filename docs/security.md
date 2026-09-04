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

