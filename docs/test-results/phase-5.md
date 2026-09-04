# Phase 5 test record

- Date: 2026-09-04 (Asia/Shanghai)
- Project version: 0.7.1
- Product baseline: `01_豆包软考私教系统_Codex开发说明书.md`, Phase 5 and sections 13–16
- Acceptance baseline: `04_验收清单.md`, sections A, B, C and I
- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS

## Automated verification

- Phase 5 package tests verify the Git-delivery entry prompt and bootstrap contract, exactly nine versioned skills, observed frontmatter, required outputs/safety boundaries, private manifest, zero scheduled writes, forbidden operations, resolved system instructions, and safe named-directory ZIP layout.
- `scripts/phase5_healthcheck.py` deterministically renders the instructions, rebuilds packages, checks deployment policy, and runs the Phase 5 tests.
- The complete repository unit suite and Git whitespace check are run at closeout; exact counts are recorded after the final run below.

## Real-account verification

| Verification | Result | Evidence |
|---|---|---|
| Nine private skills installed | PASS | Real Doubao 2.27.11 personal-skill registry and project composer showed all nine READY/enabled. |
| Skill safety state | PASS | `Ruankao Review Scheduler V1` moved from safety scanning to enabled after the client reported completion. |
| Private controller container | PASS WITH LIMITATION | New private Project `架构上岸教练` created; no separate custom-partner editor was exposed. |
| Final instruction context | PASS WITH LIMITATION | Initialization chat read and adopted the rendered instruction file; no persistent project-level instruction field was observed. |
| Feishu connector/state | PASS | Real read-only resolution and 15-table listing matched `ArchitectPass State v1`. |
| Local source anchors | PASS | PDF page and video timestamp anchors plus `611/3631 played_unchecked` progress were visible. |
| Cheko boundary | PARTIAL | No practice opened and no question/answer read; login was not re-probed in this run. |
| Browser/Baidu fallback | PASS | Authorized scopes and prior timestamp-location evidence present; no live Netdisk navigation in this run. |
| Daily/weekly same-state read | PASS WITH LIMITATION | Existing read-only jobs were visible against the same state; production names/user times remain pending. |
| Checkpoint/recovery state | PARTIAL | Protocol exists, but the first learning checkpoint waits for Phase 6 real-data initialization. |
| Existing project protection | PASS | `系统架构设计师 AI Tutor` and `pass_ai` were not modified; the accidentally surfaced parent folder was removed before save. |

Detailed real-account evidence: `artifacts/doubao-audit-logs/phase5-installation-2026-09-04.md`.

## Security assertions

- No password, cookie, OTP, token, key, Cheko question/answer, course content, or company-confidential fact was committed.
- All formal skills remain private and versioned.
- No scheduled write is enabled.
- No delete, publish, payment, permission change, or sensitive export was performed.
- The controller has no arbitrary SQL, shell, or filesystem operation.

## Final run

- `python3 scripts/phase5_healthcheck.py`: PASS (render, deterministic build, policy checks, 7/7 Phase 5 tests).
- Full repository unit suite under the bundled Python 3.12 runtime: 65/65 PASS.
- `git diff --check`: PASS at closeout.
