# Phase 5 real Doubao installation log

- Date: 2026-09-04 (Asia/Shanghai)
- Client: Doubao macOS 2.27.11
- Scope: private skill installation, isolated private project initialization, and read-only health check
- Result: `COMPLETE_WITH_DOCUMENTED_LIMITATIONS`

## Installed private skills

The real Doubao personal-skill surface showed all nine formal skills registered, enabled, and available to the new project. The surface showed 107 total skills at the time of verification. `Ruankao Review Scheduler V1` temporarily showed a safety scan; it later changed to enabled and Doubao displayed that the safety check had completed.

| Formal package name | UI state |
|---|---|
| `cheko-practice-v1` | READY / enabled |
| `ruankao-assessment-v1` | READY / enabled |
| `ruankao-case-coach-v1` | READY / enabled |
| `ruankao-controller-v1` | READY / enabled |
| `ruankao-essay-coach-v1` | READY / enabled |
| `ruankao-healthcheck-v1` | READY / enabled |
| `ruankao-materials-v1` | READY / enabled |
| `ruankao-research-verifier-v1` | READY / enabled |
| `ruankao-review-scheduler-v1` | READY / enabled after safety scan |

The composer skill picker showed these skills under the personal group. Registration was independently corroborated from the client-owned skill registry without committing the raw client preference file, cookies, tokens, or account secrets.

## Project isolation and instruction baseline

- Created a new private Doubao Project named `架构上岸教练`.
- Preserved the older `系统架构设计师 AI Tutor` project and its `pass_ai` workspace without modification.
- The initialization chat directly read these repository files from their exact allowlisted absolute paths:
  - `deployment/doubao/system-instructions-v1.md`
  - `deployment/doubao/skills-v1.json`
  - `deployment/doubao/project-v1.json`
- The chat explicitly adopted `system-instructions-v1.md` as its current control baseline.
- No separate custom-partner surface or persistent project-level instruction field was observed. The private Project remains the evidence-backed equivalent container.
- Chat evidence: Doubao conversation ID `38440213023143426` (`架构上岸教练项目初始化与健康检查`).

## Read-only health-check result

Doubao returned overall `PARTIAL`. Its headline said `PASS × 4`, `PARTIAL × 2`, `FAIL × 0`, but its detailed table contained seven checks: five PASS and two PARTIAL. This record uses the row-level result `PASS × 5`, `PARTIAL × 2`, `FAIL × 0` and preserves the headline mismatch as an observed reporting defect. Doubao reported no file modification, no state write, no schedule creation/change, no Cheko practice opening, and no question or answer read.

| Check | Result | Evidence and boundary |
|---|---|---|
| Nine formal private skills visible and usable | PASS | Nine matching directories each contain `SKILL.md`; manifest names matched; runtime mounted them. |
| `ArchitectPass State v1` | PASS | Feishu tool resolution and table listing succeeded as the user; 15 tables matched production configuration. Only table metadata and harmless aggregate record counts were read. |
| Local materials index and citations | PASS | Video index exposed `#t=`/`@HH:MM:SS`; PDF index exposed `#page=N`; existing video progress was `611/3631` seconds and remained `played_unchecked`. No live Netdisk content was read. |
| Cheko login and routes | PARTIAL | Versioned route contract was present, but this deliberately read-only run did not open practice or re-verify login. Fallback remains user login plus official export, screenshot, or compact manual import. |
| Browser/Baidu manual location path | PASS | Only the two user-authorized Baidu scopes were present in the manifest. Browser capability and prior timestamp-location evidence were visible; no live GUI navigation occurred in this run. |
| Daily/weekly schedules and state | PASS | Existing `P0-DAILY-STATE-READ` (daily 09:53) and `P0-WEEKLY-STATE-READ` (Friday 09:54) were running and read-only against the same state source. Scheduled writes remained disabled. |
| Checkpoint, backup, and pending queue | PARTIAL | No learning-session checkpoint exists yet. Backup protocol exists but no new archive was produced. Existing video index/progress remains pending real-state initialization. |

## Installation mechanics and limitations

The deterministic package format is a ZIP with a same-name top-level directory, for example `ruankao-healthcheck-v1/SKILL.md`. During this local client audit the nine source directories were registered in Doubao's per-user skill workspace, then the client was refreshed until every registry entry reported READY. This is an observed local registration mechanism, not an exposed arbitrary filesystem capability for the final controller.

The macOS native folder picker could navigate to the repository but did not reliably preserve the exact child-folder selection through computer automation. One attempt surfaced the parent `git-projects` row; it was removed before save, so no over-broad folder was bound. The new project health check instead read only three exact allowlisted absolute paths. Exact project-folder binding remains unverified.

The production-named daily and weekly templates remain pending the user's preferred times. Existing Phase 0 read-only jobs were not changed. No scheduled write is enabled.

## Sensitive-data check

This record contains no password, cookie, OTP, API key, access token, Cheko question body, Cheko answer, course file content, or company-confidential fact.
