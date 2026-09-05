# Project progress

## Phase 0 — 豆包真实能力审计

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-03 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Authority: `01_豆包软考私教系统_Codex开发说明书.md`, `02_交给Codex的总执行指令.md`, `04_验收清单.md`
- Current activity: Phase 0 through Phase 6 closed; Phase 7 continues under compressed acceptance, with the seven-day independent pilot explicitly deferred and unpassed.

### Repository initialization

- Governance files and evidence directories: created.
- Git metadata: COMPLETE — initialized as an empty repository on branch `main` after the user requested a retry on 2026-09-03.

### Evidence-backed results to date

- Real Doubao client/account/version inspected.
- Private minimal skill created; automatic and explicit invocation passed.
- Exact generated skill file and provenance captured.
- Local ZIP skill import passed with a separate canary; its explicit invocation returned `IMPORT_OK:roundtrip-001`.
- A packaged runtime probe read `references/` and `assets/` and ran a dependency-free Python script successfully.
- Private custom localhost connector installed after explicit confirmation; its MCP handshake and one exact read-only call passed in local-computer mode. Cloud-computer mode could not discover it, confirming the product's local-only boundary.
- Authorized local PDF read passed with an exact marker match.
- Doubao created, wrote, and read a private Feishu multidimensional table containing a harmless state marker plus audit/request IDs.
- Doubao created and read back a private Feishu document with exact marker/audit/request IDs; the platform's automatic generated-content block required structural cleanup and re-verification.
- After explicit confirmation, Doubao created one private Feishu calendar event and one private Feishu task, located both by title, and independently read them back with exact audit/request IDs and stable object IDs. After a second explicit confirmation, it validated the ID/title pairs, deleted only those two objects, and verified a cancelled calendar tombstone plus task `not_found`. The local Feishu weekly view did not visibly render the event before deletion, so cross-client visibility remains open.
- User-designated Baidu course scopes located and a real course player opened.
- Doubao browser skill opened and read a public test page in its side workbench.
- A real authorized Baidu course video was sought to `00:10:01`, and current/total playback times were read from the player.
- Logged-in 芝士架构 aggregate statistics, practice log, and one traceable submitted report were read in 豆包浏览器 without answering or submitting questions; official export history was empty.
- Native one-time, daily, and weekly tasks executed and each read the same Feishu state record.
- Scheduler, partner, cross-device, privacy, and diagnostic surfaces inspected.
- After explicit user confirmation, all three Doubao model-improvement data categories were disabled and read back as closed.
- Capability matrix updated and ADR-001 accepted for the Phase 0 architecture decision.

### Accepted residual limitations

- Native partner configuration and skill rollback/version history are unavailable on the observed account.
- Trusted HTTPS was not deployed because Feishu is the selected cloud state path.
- Feishu calendar client visibility, mobile continuation, and hard platform ceilings remain unproven.
- Scheduled writes remain prohibited until Phase 1 idempotency/retry tests pass.

### Exit criteria

- Complete capability matrix with status, version, identity, steps, evidence, limitations, architecture impact, fallback, and issue IDs.
- Preserve screenshots or logs for every conclusion.
- Obtain a minimal skill sample from the current UI; do not invent platform syntax.
- Record runtime/storage/connector decisions in ADR-001.
- Demonstrate a feasible path for every decision gate in specification section 7.3.

All Phase 0 exit criteria are satisfied with the limitations and fallbacks recorded in `docs/phase-0-closeout.md`.

## Phase 1 — 仓库、数据模型与状态服务

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.3.0

Delivered the canonical schemas, allowlisted state API, immutable raw-event and evidence model, reproducible mastery projection, idempotency/audit rules, backup/export/guarded restore, migration chain, offline replay reference, and 21 fake-data unit tests. A private unshared Feishu Base named `ArchitectPass State v1` was installed with all 15 logical tables. Complete canaries and a mutable profile create/update were independently read back; identical request-ID replays produced no duplicate records.

The native Feishu platform has no table-level append-only constraint, local health checks intentionally have no live Feishu credential, and scheduled writes remain disabled. See `docs/phase-1-closeout.md` for the full evidence and acceptance trace.

### Next activity

Phase 2 started with a bounded inventory and incremental manifest for only the user-authorized material scopes. No bulk upload or full reprocessing was performed.

## Phase 2 — 资料导入与可追溯检索

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.4.0

Delivered an allowlisted local material package, manifest/progress schemas, SHA-256 deduplication, page-level PDF extraction, necessary selected-page OCR, local video metadata/audio/Whisper processing, original-time subtitle offsets, bounded search results, page/time open targets, quarantine receipts, derived-write audit receipts and a Phase 2 health check.

Real probes passed on one 10-page course PDF and a 75-second range of one complete course video. Course progress is imported as an approximate half-watched low-confidence statement, supplemented by one observed `611/3631`-second position. Viewing remains `played_unchecked`, and the implemented review rule requires diagnosis before any bounded targeted rewatch.

The complete repository suite passes 33/33 tests. See `docs/phase-2-closeout.md` and `docs/test-results/phase-2.md`.

### Next activity

Phase 3 now implements the safe 芝士架构 workflow around user-authored answers: explicit practice tasks, `AWAITING_HUMAN`, post-submission result import, confidence/error capture and DOM-change fallbacks. It never answers or submits questions.

## Phase 3 — 芝士架构安全适配

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.5.0

Delivered the bounded practice-task contract, audited lifecycle, verified-route gate, `AWAITING_HUMAN`, post-submission-only import, strict content allowlists, immutable practice attempts, wrong/G review creation, versioned Cheko UI semantics and official-export/screenshot/manual fallbacks.

Real logged-in navigation passed in 豆包浏览器 for practice logs and the error book. One already-submitted historical report was imported as sanitized aggregate metadata with zero captured question bodies. Edge showed a blank practice-log content surface and is retained as a documented failure/fallback trigger.

The Phase 3 suite passes 10/10 and the complete repository suite passes 43/43. See `docs/phase-3-closeout.md` and `docs/test-results/phase-3.md`.

Phase 4 completion is recorded below.

## Phase 4 — 学习决策引擎

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.6.0

Delivered the audited fixed lifecycle, mandatory state-read gate, explainable time-bounded planning, low-energy load reduction, three-subject anti-neglect, evidence/error diagnosis, dynamic 1/3/7/14/30 review scheduling, post-submission case rubric, confirmed/redacted essay fact constraints, full essay workflow, weekly adjustment report and exam-date/progress-derived sprint mode.

The Phase 4-specific suite passes 14/14 and the complete repository suite passes 57/57. See `docs/phase-4-closeout.md` and `docs/test-results/phase-4.md`.

## Phase 5 — 豆包技能、连接器与工作伙伴安装

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.7.1

Delivered nine deterministic, versioned private Doubao skill packages; minimum-permission skill/connector/project manifests; rendered system instructions; read-only daily/weekly templates; and installation, update and rollback guidance. All nine formal skills were registered READY and enabled in the user's real Doubao 2.27.11 account. A new isolated private Project named `架构上岸教练` was created, while the older `系统架构设计师 AI Tutor` / `pass_ai` project remained untouched.

The project initialization chat read the final instruction baseline and deployment manifests from exact allowlisted paths. Its detailed real read-only health matrix returned `PASS × 5`, `PARTIAL × 2`, `FAIL × 0`; the generated headline's four-PASS count was recorded as an internal reporting mismatch. Formal skills, Feishu state, local source anchors, Browser/Baidu fallback and Phase 0 read-only schedule capability were feasible. Cheko login was intentionally not re-probed, no first learning checkpoint exists, and exact native folder binding remains unverified. Production task names/times await user confirmation; scheduled writes remain disabled.

See `docs/phase-5-closeout.md`, `docs/test-results/phase-5.md`, and `artifacts/doubao-audit-logs/phase5-installation-2026-09-04.md`.

## Phase 6 — 真实数据初始化

- Status: COMPLETE_WITH_DOCUMENTED_LIMITATIONS
- Started: 2026-09-04 (Asia/Shanghai)
- Completed: 2026-09-04 (Asia/Shanghai)
- Version: 0.8.0

Delivered and verified a Git-driven Phase 6 initialization plan, a provisional ten-node knowledge map, an optional-history profile, two authorized resource records, the observed video position, a post-submission aggregate Cheko baseline, a private runtime segment builder, an explicitly empty project-fact v1 and a runtime-budgeted seven-day plan.

In the real private Feishu Base, 15 public-safe records plus 49 private PDF/video segments were created with 64 matching audit records. Independent read-back verified every primary key, payload, hash, request ID and audit ID. A separate read-only replay returned 64/64 DEDUP_VERIFIED and changed no counts. Course text did not enter Git; historical exam information was not requested or inferred; no mastery was derived from playback, index text or aggregate results.

Official exam configuration/syllabus weights, real project facts, the first learning checkpoint and production schedule times remain explicit gaps. See `docs/phase-6-closeout.md`, `docs/test-results/phase-6.md`, and `artifacts/doubao-audit-logs/phase6-initialization-2026-09-04.md`.

### Next activity

Phase 7 should continue from revised Step D of the real 90-minute plan. The target date, optional user-provided score history, preference to skip exam-background material and Doubao Browser Cheko handoff preference are recorded; the seven-section blanket self-rating remains conversation-only and Step B is PARTIAL because recall boundaries were unknown. The first saved custom rule was invalid: stale accessibility indices in a batched dynamic-form edit persisted 3/4/13 difficulty and five years, producing a truthful inventory-shortage failure. After refreshing state between dependent actions, Codex corrected `AP-J1-计算机网络基线-v1` to 20 questions, balanced 6/10/4 difficulty, unattempted-first, computer-network only, second-edition plus must-master labels, and all 14 periods except the user's two reported exam sittings. Real generation then succeeded and loaded a practice with 20 main question stems and 21 scored answer items because a stem may contain multiple blanks.

The user randomly answered and submitted this paper with the test account, explicitly excluding it from real learning data. The visible aggregate result (`1094788`, `6 / 21`, `28.57%`, `2026-09-04 18:41:27`) now proves the ordinary UI path through result reading. Version 0.8.1 models the 20 main questions and 21 answer items separately. Its aggregate-only regression fixture generates zero learning-state writes, so J1 still requires a non-random user-authored attempt and the first real checkpoint.

The corrected adapter passes the Phase 3 health check, all 13 Cheko tests and the complete 78-test repository suite.

## Phase 7 — 测试与验收

- Status: IN_PROGRESS_COMPRESSED_ACCEPTANCE
- Started: 2026-09-04 (Asia/Shanghai)
- Version under test: 0.8.4

The real `架构上岸教练` project read the same `ArchitectPass State v1` and produced a bounded 90-minute, medium-energy plan with explicit operations, completion standards and an eight-minute checkpoint reserve. The plan phase passed, but the complete J1 loop remains `PARTIAL / AWAITING_HUMAN` because the user has not performed the learning tasks and no checkpoint has been written. An initial overclaim of J1 `PASS` was challenged and corrected in the same conversation.

Three zero-write safety probes passed: a pre-submission answer request returned `PRE_SUBMISSION_BLOCKED`; a deletion-flow test required explicit confirmation plus a verified full backup and performed no deletion; and the health check isolated a nonexistent skill sentinel as `FAIL / SKILL_MISSING` while reporting the actual system as `PARTIAL`, not broken. See `docs/test-results/phase-7.md` and `artifacts/doubao-audit-logs/phase7-acceptance-2026-09-04.md`.

The user then supplied a 2026-10-24 target exam date. The real project wrote it to the existing `user_profile` record with unique request/audit IDs and verified both the updated record and appended audit by independent read-back and hash recomputation. It correctly kept unverified official `exam_config` data empty. J1 remains `PARTIAL / AWAITING_HUMAN` at the 15-minute closed-book seven-section baseline; no mastery or checkpoint has been created.

The user later volunteered two historical score triples and a blanket 3/5 seven-section self-rating with unknown recall boundaries. Doubao safely persisted only the allowlisted optional score history, retained the original score ordering and an unverified-mapping note, and verified the update and audit hashes. It kept the self-ratings out of mastery/state tables, marked Step B PARTIAL, and advanced only to the Step C video-and-recall human gate. A transient pre-write calculation timeout recovered by retry without a duplicate write.

The user subsequently confirmed that they have already taken the exam and do not need exam-introduction background. Doubao reclassified Step C as `SKIPPED_BY_USER / NOT_NEEDED_FOR_CURRENT_GOAL`, safely stored the user-provided constraint with unique request/audit IDs, and independently verified both records and hashes. The 611-second video position remains `played_unchecked`; no learning completion, mastery or checkpoint was inferred. Its 20 minutes were reassigned to Cheko and case practice without exceeding the original 90-minute session cap. J1 remains `PARTIAL / AWAITING_HUMAN` at the user-controlled Cheko practice gate.

The Cheko handoff is now configured for Doubao Browser. The allowlisted preference write and audit passed independent read-back with prior constraints preserved. An initial real read-only project-agent probe observed a logged-in `www.cheko.cc` home surface with personal practice progress and a visible `自定义组卷` entry, but its attempts to inspect the configuration triggered `/anti-hack`; no bypass was attempted. Doubao may read only visible post-submission aggregates after the explicit `已提交` signal, with screenshot/manual aggregate entry as fallback. The initial probe performed zero business-state writes, opened no question and created no mastery/checkpoint.

Direct ordinary UI operation in the existing Doubao Browser later reached the form without bypassing protection and verified all available filter groups. An initial invalid save and visible inventory-shortage error exposed stale-index handling in dynamic forms; the rule was corrected with refreshed state between dependent UI actions. `出题` then visibly succeeded and opened the practice page without any answer or submission action. The second authorized Baidu material root was also enumerated: eight PDFs are present, including explicit choice and case `真题分类解析` titles. These entries are inventory-only until downloaded, hashed and content-verified. Phase 7 now waits for the user to answer and submit the generated paper.

The user subsequently randomized and submitted that paper solely as a test-account flow probe. Codex observed only the post-submission aggregate (`test_id=1094788`, `6 / 21`, `28.57%`, timestamp `2026-09-04 18:41:27`). The paper's 20 configured main questions expanded to 21 scored answer items because a stem can contain more than one blank. The corrected adapter and regression fixture preserve those two counts separately and emit zero learning writes. Phase 7 therefore waits for a genuine user-authored learning attempt, not another infrastructure probe.

At the user's request, non-time-dependent validation now continues without waiting for the seven-day independent pilot. The pilot remains `DEFERRED / NOT_RUN` and cannot be counted as PASS at final sign-off. A deployment-only checkpoint was created in real Feishu with unique request/audit IDs, independently verified, then recovered after Codex actually quit and reopened the real Doubao client. The reopened recovery was read-only and reproduced the exclusion of workflow-test result `1094788`; all four learning tables remained empty. The J `退出重开` path is PASS for deployment recovery, not for a completed learning session.

Version 0.8.2 also adds a checksum-protected persistent offline outbox. Restart retention, failed-send retention, acknowledgement-only removal, request/audit preservation, path confinement, operation allowlisting, idempotency conflicts and tamper rejection pass. The complete repository suite now passes 81/81; a deliberately induced real Doubao-to-Feishu outage is still pending.

Commit `b6f1ad1` corrected a clean-bootstrap ordering defect by restricting Phase 1 to its own state, backup, outbox and migration tests. A fresh directory populated only from `git archive HEAD` then passed Phase 1, 3, 4, 5 and 6 health checks. Its complete unit suite passed all 81 tests with two expected skips for private PDF/video runtime catalogs that are intentionally absent from Git. This establishes `CLEAN_GIT_SNAPSHOT_BOOTSTRAP_PASS`; a clone from a real private remote is still pending because no remote URL has been configured.

The real Doubao project then generated the same weekly-report preview twice from independently re-read Feishu state. In both runs, before/after counts remained `audit_log=72`, `study_events=3`, and all practice/mastery/review tables `0`; no `weekly_reports` table exists. Both runs excluded canaries, the deployment-only recovery checkpoint and randomized result `1094788`, diagnosed the same case/essay underinvestment and watch-without-output risk, selected the same three priorities, and wrote zero records. Run 2 truthfully surfaced and recovered from one response-shape parsing error. Result: `SAME_STATE_WEEKLY_REPORT_SCENARIO=PASS`; actual scheduled delivery is still pending and is not claimed.

The same real project also validated the Cheko manual aggregate fallback while the attached browser panel visibly hit `/anti-hack`. It accepted the excluded workflow-test aggregate, distinguished 20 main stems from 21 scored blanks/items, verified `6/21=28.57%`, and generated a zero-write dry-run. Before/after remained `practice_attempts=0`, all mastery/review tables `0`, `study_sessions=1`, and `audit_log=72`; no private API or question/answer content was used. Result: `CHEKO_MANUAL_AGGREGATE_FALLBACK=PASS`, without claiming learning progress.

Direct inspection of Doubao's native schedule list then corrected the scope of earlier schedule evidence. The only active entries are `P0-DAILY-STATE-READ` at 09:53 daily and `P0-WEEKLY-STATE-READ` at 09:54 Friday, both reading `ArchitectPass Phase0 State Probe`; the completed one-time entry is also Phase 0. No schedule targets production `ArchitectPass State v1`. The J scheduled-weekly-report item is therefore `NOT_CONFIGURED`; creating it awaits an explicit time/notification choice, and no schedule was changed during this read-only audit.

After the user selected Saturday 20:00, Codex created the production native task `架构上岸教练-每周只读复盘-v1`. The schedule list visibly read it back under `进行中` as `每星期六 • 20:00`, with a prompt bound to private `ArchitectPass State v1` and explicit zero state/audit writes. Git deployment manifest and prompt now match the installed task; Phase 5 health and all 82 repository tests pass. Result: `PRODUCTION_WEEKLY_TASK_CONFIGURED_PASS`; actual time-triggered delivery remains pending, and the daily production reminder still has no user-selected time.

Codex used the same task's native `立即运行` menu and verified a real scheduler-dispatched report against the active 15-table production Base. It read `audit_log=72`, excluded the canaries, deployment checkpoint, randomized workflow test, aggregate-only baseline and unchecked playback, reported zero valid learning activity, and emitted exactly three priorities without any observed write. The first output also exposed a truncated internal Base identifier, so Codex tightened both live and Git prompts to forbid full or partial internal identifiers, URLs and links. The hardened task was saved and visibly read back with Saturday 20:00 unchanged. Doubao deduplicated the immediate second dispatch, so `PRODUCTION_WEEKLY_NATIVE_RUN_NOW=PASS`, but post-hardening redaction verification and the first natural trigger remain pending; Phase 7 J stays PARTIAL.

Version 0.8.4 completed a deterministic seven-logical-day functional simulation without touching authoritative state. All 19 checks passed, covering daily checkpoints, restart recovery, overdue review, low-confidence G, targeted rewatch, case/essay gates, three-subject work, weekly reporting, offline restart/replay, mastery reproducibility and backup exports. The exercise found and fixed two real defects: `P7-SIM-001` added the missing audited review-completion transition, and `P7-SIM-002` removed an eager optional-PDF dependency that initially prevented the real Doubao local sandbox from starting the script. After the fix, the real `架构上岸教练` project independently ran the repository script and reported PASS with zero production writes, external calls or Cheko answer/submission actions. This is accelerated functional evidence only; the mandatory real seven-day independent pilot remains `DEFERRED / NOT_RUN`.

## Final Windows delivery acceptance — 2026-09-05

Status: `PASS_WITH_LIMITATIONS`. Final main is `567e3b8` (1.1.1). Windows run `33942450273` on core code `2a28bd6` passed installation, 95 regression tests (92 pass, 3 expected optional/private-data skips), and a no-Git/no-Python-on-PATH offline clean installation in Chinese/space paths, including PDF indexing, repeat execution and relocated restart. Final main passes all 95 local Mac tests and all 19 accelerated seven-logical-day checks. This is not a real seven-day unattended pilot.

The authorized temporary Actions write permission was used only for the isolated `codex/windows-acceptance` logs branch. Commit `3988fe1` restored workflow `contents: read`, removed the branch writer, and was pushed before final packaging. Repository-wide default permission settings were not changed.

Real Doubao created an isolated project and 15-table Feishu test Base, verified empty-profile initialization and zero-growth replay, wrote a clearly simulated training checkpoint, then recovered from persistent configuration in a fresh local-computer conversation (five mastery records, three pending reviews, actual PDF page extraction, zero recovery writes). Codex supplied the equivalent of a user selecting the desktop local-computer mode/project and the directory-based recovery prompt; this is not a no-assistance install or proof of native project-level file binding. Existing-account skills were reused when identical.

The final private artifact is `dist/delivery/final/architectpass-offline-1.1.1.zip` (26,710,010,690 bytes), containing all 349 authorized files, nine skills, Windows embedded Python with eight wheels, and the Mac runtime. Actual archive verification passed, every tracked source file matches final main, there are zero missing materials/duplicate members/separate SHA files and no test-user state. Earlier same-version packages are process candidates, not the final delivery.

Remaining limits are explicit: first login/system permissions and local mode selection require user participation; fresh conversations without verified project binding need the local project path; Cheko anti-hack uses official/manual-result fallback; full Windows OCR/ASR, a newly registered account, Windows Doubao GUI installation, natural-time reminders and a real seven-day pilot are not claimed. Health checks now exclude unrelated-project reminders and non-required Baidu login in offline mode. Full report: `docs/test-results/final-delivery-windows-2026-09-05.md`.

## Public source Windows entry — 2026-09-05

Status: `PUBLIC_SOURCE_RUNTIME_PASS / WINDOWS_GUI_NOT_TESTED`. User made the repository public and accepted public development history. Main `6d29e7f` (1.1.2) now supplies a PowerShell-only anonymous source ZIP installer: fetch-only, baseline reading, project-private runtime preparation, six health checks and nine skill ZIPs. No Git, SSH, GitHub login, system Python or user-entered commands are required by this path. Replays preserve the source snapshot and user files; main downloads retain an honest unknown commit ID.

All 98 local tests passed. Both Windows run `33944820371` and final run `33944955067` succeeded; the final run additionally verified the default main ZIP path without Git/Python/uv on PATH. CI remains repository-read-only. Baidu instructions prefer the preinstalled logged-in official Windows client, keep browser/client sessions distinct and separate shared material access from new-user learning state. Actual Windows Doubao and Netdisk GUI permissions/control remain unverified and have explicit user-guided fallbacks. The existing 1.1.1 full materials ZIP was not rebuilt or overwritten by this entry-only change. See `docs/test-results/public-source-bootstrap-windows-2026-09-05.md`.

## Artifact cleanup and local Mac experience — 2026-09-05

Status: `LOCAL_RUNTIME_PASS / FORMAL_SESSION_PENDING_UNLOCK`. Main `939c4bf` (1.1.3) fixes offline startup for an existing uv-created private environment without pip by seeding pip with that interpreter's ensurepip. Actual Mac startup now completes all six checks without failure (Phase 1 remains PARTIAL pending live Feishu verification); all 99 unit tests pass. No system Python was modified.

Three obsolete archive candidates and the old acceptance extraction were moved to a dedicated recoverable Trash folder (approximately 81 GB; Trash not emptied). Unique acceptance outputs were archived first. The final 1.1.1 delivery ZIP and both original course directories were preserved. The development worktree now resides at ignored `dist/development-history`, with a local navigation guide at `dist/本机体验与产物导航.md`.

The real Doubao project was visibly opened, but macOS locked before a fresh formal experience task could be created or its prompt sent. User unlock is required to continue; no new real learning evidence was fabricated or recorded. Gitee support and rebuilding the full materials ZIP are outside this cleanup. See `docs/test-results/mac-experience-preparation-2026-09-05.md`.

After the user unlocked the Mac, status advanced to `FORMAL_EXPERIENCE_READY / AWAITING_USER_STUDY_INPUT`. A fresh local-computer task in the real project completed state/material checks and asked for today's available minutes and energy. Doubao distinguished the production 15-table Base from a same-name empty Base and excluded test state; local binding existence, 0600 permissions and Git exclusion were independently verified. No learning answers or actual study evidence were fabricated. The first real learning loop remains for the user to perform. The three visible read-only schedules include legacy probes and do not establish a production daily reminder.

## Recipient deployment self-login loop — 2026-09-05

Status: `PROTOCOL_REGRESSION_PASS / RECIPIENT_RECOVERY_PENDING`. The user reports Doubao waiting for another Doubao login in a virtual desktop, without an error. Main `dec2d0c` (1.1.4) removes the website self-control fallback, scopes Codex development instructions, adds a shared local-context/identity gate and preserves completed installation state on resume. Unavailable self-UI now requires a specific user click, not another Doubao session. README and generated offline prompts carry the same boundaries. All 102 local tests and Phase 5 regeneration/build checks pass. Existing 1.1.1 materials ZIP and Gitee were not updated. No remote recipient UI trace was obtained and no zero-assistance end-to-end pass is claimed. See `docs/test-results/doubao-self-login-recovery-2026-09-05.md`.
