# Phase 1 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.3.0
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`
- Acceptance baseline: `04_验收清单.md` sections B and C
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated unit tests

Command: `PYTHONPATH=backend python3 -m unittest discover -s tests/unit -v`

Final result: 21/21 PASS.

Covered: profile read/write, idempotent replay, request-ID conflict, immutable raw events, traceable source validation, failed-write audit, mastery ceiling for viewing, low-confidence risk, pending-review deduplication, checkpoint completeness, operation allowlist, delete confirmation/backup gate, JSON/CSV/Markdown export, backup checksum/path validation and offline replay acknowledgement.

## Real Feishu deployment

`ArchitectPass State v1` was installed as a private, unshared Base with all 15 logical tables. Two complete, source-anchored canaries were appended and independently read back. Replaying their identical request IDs returned one record each and added nothing. See `artifacts/doubao-audit-logs/phase1-feishu-deployment-2026-09-04.md` and `deployment/feishu/production-v1.json`.

Native Feishu does not provide the required append-only table constraint, so it is enforced by the allowlisted workflow. A real harmless profile record then passed create, read, update, audit append and independent read-back with stable record IDs and before/after hashes. Scheduled writes remain disabled. The captured harmless state is stored as a checksummed backup fixture and verified by the automated suite.

## Final verification

- `python3 scripts/phase1_healthcheck.py`: schema PASS, migration PASS, 15-table deployment evidence PASS, unit tests PASS; local live Feishu probe truthfully PARTIAL because authentication is platform-managed.
- `PYTHONPYCACHEPREFIX=/private/tmp/architectpass-pycache python3 -m compileall -q backend scripts tests`: PASS.
- `git diff --check`: PASS.
