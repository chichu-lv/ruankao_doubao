# Doubao capability matrix

Audit environment: user's real macOS computer, real Doubao personal account, real Feishu and Baidu Netdisk clients, real Edge session, and real 芝士架构 account.  
Audit dates: 2026-09-03 to 2026-09-04.  
Doubao version: 2.27.11 (2.27.11).  
Identity: personal Doubao account, standard subscription; identifiers are intentionally redacted.

Status meanings: PASS = native requirement demonstrated; PARTIAL = usable with a documented limitation; FAIL = observed unavailable; UNKNOWN = not yet exercised to a defensible conclusion.

| ID | Capability | Status | Actual result and evidence | Architecture impact / fallback | Issue |
|---|---|---:|---|---|---|
| DB-001 | PC client install and login | PASS | Installed client opened; account and version recorded. Evidence: `artifacts/doubao-audit-screenshots/DB-001-client-version.png`. | Use Doubao desktop as the user-facing controller. | - |
| DB-002 | Private work partner | FAIL | `我的伙伴` was empty and no private custom-partner creation entry was found on the standard-plan surface. Evidence: `DB-002-my-partners-empty.png`. | Use a private Doubao Project plus private skills as the equivalent persistent entry; re-test after account/client changes. | P0-002 |
| DB-003 | Partner persona/model/permission persistence | FAIL | Partner editor was unavailable; Project edit only exposed name and local-folder attachment. | Store persona/instructions in the private Project and skill set; keep model/permission selection explicit per task until persistence is proven. | P0-003 |
| DB-004 | Create minimal custom skill | PASS | Created private `phase0-capability-probe`; it is listed under personal skills. Evidence: `DB-004-created-skill-listed.png`. | Skill is a viable workflow carrier. | - |
| DB-005 | Import local skill file | UNKNOWN | `上传技能` entry exists, but no import round trip has been executed. | Keep the captured actual sample ready for a later import test. | P0-005 |
| DB-006 | Actual `SKILL.md` format | PASS | Exact generated file and provenance are preserved under `artifacts/doubao-skill-samples/phase0-capability-probe/`. | Build future skills from this real format, not an assumed schema. | - |
| DB-007 | Script runtime and dependencies | PARTIAL | Generator created `scripts/`; validator failed because `yaml` was absent. Language, sandbox, and network limits are not fully characterized. | Prefer dependency-free skills; isolate script probes before implementation. | P0-007 |
| DB-008 | References and templates | PARTIAL | Generator created `references/` and `assets/`, but runtime use was not exercised. | Treat these directories as format-supported but behavior-unproven. | P0-008 |
| DB-009 | Manual and automatic skill invocation | PASS | Automatic: `PHASE0_OK:auto-match-001`; explicit: `PHASE0_OK:manual-001`. Evidence: corresponding DB-009 screenshots. | Both routing paths are viable. | - |
| DB-010 | Skill update/rollback/remove | UNKNOWN | Creation and invocation passed; update, rollback, version display, and removal remain untested. | Version skills in Git and retain a reinstall path; do not rely on native rollback yet. | P0-010 |
| DB-011 | Custom connector creation | PARTIAL | Form supports name, HTTP transport, URL, and headers; existing Baidu connector is visible. No connector was saved. Evidence: `DB-011-014-custom-connector-form.png`. | A restricted HTTP connector is plausible, but not a passed runtime path. | P0-011 |
| DB-012 | Localhost connector access | UNKNOWN | Local probe server could not bind because the managed audit sandbox denied the port; Doubao itself was not reached. | Re-run with a user-started probe or use trusted HTTPS. | P0-012 |
| DB-013 | Trusted HTTPS connector access | UNKNOWN | No trusted endpoint has been registered and called. | Provide a least-privilege HTTPS state service if native Feishu access is insufficient. | P0-013 |
| DB-014 | Authentication and secret storage | PARTIAL | Custom headers exist; no separate OAuth/vault control was visible. No secret was entered. | Keep secrets out of prompts and Git; prefer platform-managed OAuth or server-side secrets. | P0-014 |
| DB-015 | Feishu document read/write | PARTIAL | Signed-in Feishu account created/saved/read a private document body marker. Doubao-to-Feishu access is not yet proven. Log: `phase0-observations-2026-09-04.md`. | Feishu is a candidate state/report layer only after Doubao access is verified. | P0-015 |
| DB-016 | Feishu sheet and multidimensional table read/write | PARTIAL | Spreadsheet cell readback passed; multidimensional-table import reported one record written. Doubao path remains untested. | Candidate structured state layer; retain external HTTPS alternative. | P0-016 |
| DB-017 | Feishu drive file management | PARTIAL | New private cloud objects were created in the personal space; specified-folder and Doubao operations were not tested. | Use a dedicated private folder after access path is confirmed. | P0-017 |
| DB-018 | Feishu calendar and tasks | UNKNOWN | Surfaces are present; no create/update round trip yet. | Doubao scheduler remains the immediate reminder candidate. | P0-018 |
| DB-019 | Read authorized local file | PASS | Doubao read the PDF probe and returned exact marker `ARCHITECTPASS_LOCAL_FILE_PROBE_20260903`. | Local PDF ingestion is viable for explicitly attached files. | - |
| DB-020 | Authorized directory access/listening | PARTIAL | Doubao Project can attach a local folder; directory watcher behavior was not tested. | Use explicit project folder and incremental manual/import triggers until watcher support is proven. | P0-020 |
| DB-021 | Open/control browser | PARTIAL | Browser and external-browser settings exist; accessibility/screen-recording permissions were off and Doubao-driven control was not completed. | Use guided manual navigation and screenshot/import fallback. | P0-021 |
| DB-022 | Baidu Netdisk login and handoff | PASS | Real client was logged in and private files were visible; no CAPTCHA was encountered. | Existing session is usable; hand off OTP/CAPTCHA to user if encountered. | - |
| DB-023 | Open specified Baidu course | PASS | Both user-designated useful course scopes were located; a course video opened. | Name-based course retrieval is viable. | - |
| DB-024 | Seek Baidu video time | PARTIAL | Player opened, but exact automatic seek was not proven. | Provide exact video name plus timestamp for user positioning. | P0-024 |
| DB-025 | Read visible playback progress | UNKNOWN | Player controls/progress were not exposed reliably in the accessibility tree. | Ask user for progress or import a screenshot; never infer watched state. | P0-025 |
| DB-026 | 芝士架构 login and handoff | PASS | Logged-in avatar and nonzero account progress were visible in Edge after user confirmation. | Reuse authorized browser session; user handles OTP/CAPTCHA. | - |
| DB-027 | Open chapter/year/error book | PARTIAL | Chapter progress and navigation entries were readable; route/click behavior was unstable in this run. | Give exact manual path; preserve screenshot-based fallback. | P0-027 |
| DB-028 | Read result-page statistics | PARTIAL | Homepage chapter completion counts were extracted; a submitted-result page was not inspected. | Import visible summary, screenshot, or user-provided result after submission. | P0-028 |
| DB-029 | Official export flow | UNKNOWN | `一键导出` was visible but not exercised; no export file obtained. | Prefer official export when available; otherwise screenshot/manual import. | P0-029 |
| DB-030 | Page-change fallback | PASS | Visible progress can be read from screenshots/accessibility output without private APIs. | Maintain screenshot and manual-result schemas. | - |
| DB-031 | One-time scheduled task | UNKNOWN | Scheduler exists; no task created/executed. Evidence: `DB-031-scheduler-surface.png`. | Pending real execution test. | P0-031 |
| DB-032 | Daily scheduled task | UNKNOWN | Scheduler exists; state read and idempotency not tested. | Pending real execution test against shared state. | P0-032 |
| DB-033 | Weekly scheduled task | UNKNOWN | Scheduler templates exist; no weekly report executed. | Pending real execution test against shared state. | P0-033 |
| DB-034 | Scheduled retry and idempotency | UNKNOWN | No failure/retry run executed. | Every future write must include request/audit IDs and deduplication. | P0-034 |
| DB-035 | Cross-device visibility | PARTIAL | Remote-control UI describes same-account mobile continuation and notifications; no phone round trip. Evidence: `DB-035-cross-device-remote-control.png`. | Treat mobile as optional until end-to-end test passes. | P0-035 |
| DB-036 | File size/count limits | PARTIAL | Feishu AI paste displayed 10,000-character text and 10 MB image limits; broader Doubao limits remain unknown. | Chunk inputs and record per-surface limits as observed. | P0-036 |
| DB-037 | Task duration/frequency limits | UNKNOWN | No boundary test performed. | Design resumable checkpoints and backoff. | P0-037 |
| DB-038 | Context and long-term history | PARTIAL | Tasks persist in history; long-term retention and context boundaries are unmeasured. | Store authoritative state outside chat history. | P0-038 |
| DB-039 | Failure information and task history | PASS | Step status, history, approval prompts, and explicit errors were visible during the audit. | Record audit IDs and surface failures truthfully. | - |
| DB-040 | Model-improvement privacy setting | PARTIAL | All three improvement categories were observed enabled; user choice has not yet been applied. Evidence: `DB-040-model-improvement-settings.png`. | Do not upload sensitive material until the user chooses the desired setting. | P0-040 |

## Section 7.3 decision-gate status

| Decision gate | Current path | Gate |
|---|---|---:|
| Private partner or equivalent persistent configuration | Private Doubao Project + private skill set | FEASIBLE, constrained |
| Custom skill/workflow carrier | Real private skill with manual and automatic invocation | PASS |
| Persistent read/write state | Feishu write surfaces proven, but Doubao access to them is not yet proven; restricted HTTPS remains untested | NOT YET PASSED |
| Material retrieval | Authorized local PDF and named Baidu folders | PASS |
| 芝士架构 result import | Screenshot/manual visible-stat extraction works; official export/result page incomplete | FEASIBLE, constrained |
| Scheduled reminder | Native scheduler UI exists; real one-time/daily/weekly execution incomplete | NOT YET PASSED |

Large-scale implementation remains blocked until the state-storage and scheduling gates have evidence-backed paths.
