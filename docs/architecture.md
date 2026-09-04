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
- A transport failure remains a failure. The payload may enter the checksum-protected persistent outbox, but must not be reported as committed. Each queued write retains its original request ID, audit ID and actor; only an acknowledged `status=ok` removes it.
- Replaying the same request ID and payload returns the first result. Reusing it for another payload fails with `IDEMPOTENCY_CONFLICT`.
- Scheduled jobs are read-only until real scheduled-write retry/deduplication behavior is tested.

## Adapter boundary

`backend/architectpass_state` is deliberately provider-independent. `InMemoryStore` is a fake/reference adapter for unit tests. `PersistentOfflineOutbox` writes only inside a caller-authorized existing directory, uses atomic replacement and mode `0600`, and rejects path escape, tampering, request-ID conflicts and non-allowlisted operations. The Feishu mapping in `schemas/feishu-bitable-v1.json` is the production contract; the private Doubao workflow performs the actual table operations. A trusted HTTPS adapter remains the documented fallback if Feishu constraints later block a required operation.

## Safety boundaries

- No API exposes arbitrary SQL, shell commands, filesystem paths, or browser selectors.
- Source anchors are structured: PDF page, video time, visible Cheko result/test ID, or original web URL.
- Original course videos and full Cheko question banks never enter the state layer.
- Deletion requires an explicit confirmation and a verified backup reference; immutable facts are not deleted by ordinary operations.

## Phase 2 local material plane

The private material plane is separate from authoritative Feishu state. It retains large copyrighted inputs locally and exposes only bounded, source-traceable retrieval results to Doubao.

```text
Authorized Baidu/local file
        |
        v
SHA-256 manifest + allowlisted importer
        |
        +--> PDF pages --> selected-page OCR --> page citation/open target
        |
        +--> video metadata --> bounded audio --> local SRT --> original-time citation
        |
        v
Private ignored catalog --> bounded snippet + filename/page-or-time/confidence
```

- PDF pages retain checksum, page number, extraction confidence and OCR flag.
- Video clips retain a non-negative offset so subtitle times map back to the original video timeline.
- Original video SHA-256 is used in citations even though the transcript has its own checksum.
- Raw text is stored in the private catalog; search responses contain bounded snippets rather than the full document or transcript.
- Baidu automation failure does not block study: filename plus page/timestamp is the stable fallback.
- `played_unchecked` is a progress fact, not mastery evidence. Review planning starts with diagnosis and can only create bounded weak-range rewatch targets.

## Phase 3 Cheko human boundary

```text
Doubao creates bounded practice task
        |
        v
verify allowlisted Cheko route
        |
        v
AWAITING_HUMAN  -- user answers and submits --> post-submit result
        |                                          |
        | no answer/submit operation                v
        +------------------------------> allowlisted metadata import
                                                   |
                         immutable attempt + evidence + review queue
```

- Browser selectors are versioned accessible semantics plus route assertions, not persisted transient node IDs.
- Import sources are limited to visible submitted report, official export, post-submit screenshot and manual summary.
- Unknown fields, raw HTML, question text, options, answers and explanations are rejected recursively.
- Wrong answers require K/C/M/A/Q/T/E; low-confidence correct answers are normalized to G.
- The Cheko adapter returns state-layer write intents; authoritative persistence continues through the Phase 1 Feishu contract.

## Phase 4 learning controller

```text
complete state snapshot
        |
        v
OBSERVE -> DIAGNOSE -> PLAN -> EXECUTE -> TEST -> UPDATE -> SCHEDULE -> CHECKPOINT
                              |           ^
                              +-- AWAITING_HUMAN (user answers/submits)
```

- Planning is impossible without a timestamped read containing profile, exam date, due reviews, 7/14/30-day score windows, progress, three-subject ratios and prior incomplete work.
- Candidate ranking retains the exact six-factor base formula and logs distinct balance/energy multipliers. Plans reserve checkpoint time and cannot exceed the available budget.
- The controller holds no browser answer or submit operation. It accepts only a post-action user-output reference before assessment.
- Review dates start from 1/3/7/14/30 days and move according to evidence strength, confidence, importance, error severity and exam date.
- A pending review is closed only through allowlisted `complete_review`, with an ISO completion time and traceable evidence reference; the completed item no longer blocks a later review for the same topic and type.
- Case grading is post-submission and source-bound. Essay organization is limited to confirmed, redacted fact IDs; missing or unknown facts cannot be fabricated.
- Weekly reports are derived read models. Sprint activation is a function of exam date and syllabus progress, not a hard-coded calendar threshold.
