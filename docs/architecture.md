# ArchitectPass architecture

## Phase 1 decision

Doubao desktop remains the only conversational controller. The authoritative structured state is a private Feishu multidimensional table set because Phase 0 proved that foreground Doubao and native scheduled tasks can read the same record. Local code provides the canonical contract, validation, deterministic derivation, offline outbox, export and backup verification. It is not a second authoritative database.

```text
Doubao private Project / private skills
        |
        | allowlisted logical operations
        v
ArchitectPass state contract
  - validate input and source anchors
  - require request_id + audit_id
  - preserve raw facts
  - derive mastery reproducibly
        |
        v
Private Feishu Bitable (authoritative)
        |
        +--> verified JSON/CSV/Markdown backup (local, user-owned)
        +--> idempotent offline outbox (only while unavailable)
```

## Truth and consistency

- `study_events` and `mastery_evidence` are immutable facts.
- `mastery_state` is a replaceable projection identified by `rule_version` and the exact evidence IDs used.
- A write succeeds only after payload validation, request-ID deduplication, append-only audit, and read-after-write verification by the Feishu workflow.
- A transport failure remains a failure. The payload may enter the outbox, but must not be reported as committed.
- Replaying the same request ID and payload returns the first result. Reusing it for another payload fails with `IDEMPOTENCY_CONFLICT`.
- Scheduled jobs are read-only until real scheduled-write retry/deduplication behavior is tested.

## Adapter boundary

`backend/architectpass_state` is deliberately provider-independent. `InMemoryStore` is a fake/reference adapter for unit tests. The Feishu mapping in `schemas/feishu-bitable-v1.json` is the production contract; the private Doubao workflow performs the actual table operations. A trusted HTTPS adapter remains the documented fallback if Feishu constraints later block a required operation.

## Safety boundaries

- No API exposes arbitrary SQL, shell commands, filesystem paths, or browser selectors.
- Source anchors are structured: PDF page, video time, visible Cheko result/test ID, or original web URL.
- Original course videos and full Cheko question banks never enter the state layer.
- Deletion requires an explicit confirmation and a verified backup reference; immutable facts are not deleted by ordinary operations.

