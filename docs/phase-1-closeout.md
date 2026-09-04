# Phase 1 closeout

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Date: 2026-09-04 (Asia/Shanghai)
- Version: 0.3.0
- Authority: product specification Phase 1; acceptance checklist sections B and C

## Delivered

| Deliverable | Result | Evidence |
|---|---|---|
| Repository and governance | PASS | `AGENTS.md`, `README.md`, `CHANGELOG.md`, `VERSION`, `.env.example` |
| Canonical data contract | PASS | `schemas/state-contract.schema.json`, `schemas/feishu-bitable-v1.json`, `docs/data-dictionary.md` |
| State read/write API | PASS | `backend/architectpass_state/service.py`; real profile create/read/update/read-back |
| Idempotency and audit | PASS | request fingerprint tests; real Feishu replay returned exactly one record per request ID |
| Raw facts vs derived mastery | PASS | immutable event/evidence tables and reproducible `mastery-v1` projection |
| Backup/export/restore | PASS | checksummed JSON plus CSV/Markdown export; guarded restore with stale-backup rejection |
| Migration | PASS | backup-gated `0001-initial` and validated ordered migration chain |
| Offline replay | PASS | acknowledgement-gated outbox and restored idempotency reconstruction tests |
| Fake-data unit tests | PASS | 21/21 tests |
| Formal private Feishu topology | PASS | one unshared Base, 15 stable table IDs, independent schema and record read-back |
| One-command health check | PASS WITH BOUNDARY | validates code, schema, migration and captured deployment; correctly reports no local live Feishu authentication |

## Real-state evidence

- Private Base: `ArchitectPass State v1`
- Deployment manifest: `deployment/feishu/production-v1.json`
- Real UI audit: `artifacts/doubao-audit-logs/phase1-feishu-deployment-2026-09-04.md`
- Checksummed harmless snapshot: `tests/fixtures/phase1-feishu-canary-backup.json`
- Snapshot checksum: `39cbc84f111b789a8feeed4fb2f43531f66ddd3850ae9ab900e7e11732d9e477`

## Acceptance trace for Phase 1 scope

| Checklist item | Result | Issue / limitation |
|---|---|---|
| B: schema, migration, backup and restore | PASS | none |
| B: every write has request ID | PASS | application protocol; no native Feishu unique constraint |
| B: audit and rollback path | PASS | hashes plus backup reference; destructive production restore still requires action-time confirmation |
| B: unit/integration/e2e/security tests | PARTIAL | unit complete; later-phase integration, end-to-end and security suites remain future gates (`P1-L01`) |
| B: one-command health check | PASS WITH BOUNDARY | local command cannot authenticate to Feishu (`P1-L02`) |
| C: profile read/write | PASS | harmless real record only |
| C: exam config source/date | SCHEMA PASS | real official exam facts intentionally not invented; populated in later import (`P1-L03`) |
| C: events and derived mastery separated | PASS | none |
| C: review deduplication | PASS | fake adapter unit test; real scheduled writes remain disabled |
| C: checkpoint create/recover | PASS | local contract/unit test; Doubao workflow packaging is later phase |
| C: scheduler reads same state | PASS | Phase 0 native schedule evidence plus Phase 1 same private Feishu topology |
| C: JSON/CSV/Markdown export | PASS | harmless captured snapshot verified |
| C: failures are truthful | PASS | stable error envelope and failed-write audit |
| C: offline replay | PASS | in-process reference outbox; persistent adapter is a later deployment concern (`P1-L04`) |

Post-closeout update (v0.8.2): `P1-L04` is closed for local persistence. `PersistentOfflineOutbox` survives restart, retains unsuccessful sends, removes only acknowledged sends, preserves request/audit context, and rejects tampering, path escape, request conflicts and non-allowlisted operations. A real Doubao-to-Feishu outage remains a Phase 7 integration check rather than a local-persistence gap.

## Documented limitations

1. Feishu Bitable exposes no native append-only table constraint. All writers must use the bounded workflow; ordinary users must not edit raw fact tables manually.
2. The first bootstrap canaries lacked timestamp and content hash. They remain as truthful immutable history and were superseded by complete records rather than modified or deleted.
3. The local health command deliberately has no Feishu credential. Live Feishu evidence comes from the real Doubao connector read-back, and a disconnected connector is reported as `PARTIAL`, never `PASS`.
4. Scheduled writes remain disabled until retry timing is characterized in the scheduler integration phase.

Phase 2 may begin. None of these limitations authorizes large-scale source ingestion, course uploading, Cheko scraping, or automatic question answering.
