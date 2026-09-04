# ArchitectPass / 架构上岸教练

一个由 Codex 开发和部署、以豆包工作私有工作伙伴为最终主控的“系统架构设计师”备考系统。

## 豆包一键初始化

最终交付入口是本 Git 仓库，不依赖开发电脑上预先配置的豆包状态。把私有仓库链接发给已登录的豆包，并发送这一条启动提示词：

```text
请从这个私有 Git 仓库部署“架构上岸教练”：<你的私有 Git 仓库链接>。完整阅读根目录 README.md，并严格执行“豆包一键初始化”所引用的自举协议；创建全新的私有项目，不修改任何已有项目。完成后运行只读健康检查，按 PASS/PARTIAL/FAIL 报告证据和降级路径。
```

豆包必须继续执行 [Git 驱动自举协议](deployment/doubao/bootstrap-v1.md)：读取不可省略的产品与验收基线，构建九个技能包，创建隔离的私有项目，安装技能，接入私有状态层，在用户确认执行时刻后配置只读任务，并运行真实健康检查。仓库不可读取时，只应要求用户通过官方界面登录，不能索取密码、Cookie 或令牌。

## 当前阶段

`Phase 6 — 真实数据初始化：已完成（含已记录限制）`

真实账号审计、状态层、本地资料管线、芝士架构安全适配、学习决策引擎、豆包私有部署和真实数据初始化已经完成。九个正式技能已启用；授权资料、页码/时间戳索引、视频进度、暂定知识图和已提交芝士聚合基线已写入同一私人状态层。豆包仍是唯一日常对话主控。

## 权威基线

- `01_豆包软考私教系统_Codex开发说明书.md`：产品与工程规格
- `02_交给Codex的总执行指令.md`：总执行指令
- `04_验收清单.md`：不可省略的验收标准
- `05_豆包能力审计矩阵模板.csv`：Phase 0 审计清单

## Phase 0 输出

- `docs/doubao-capability-matrix.md`
- `docs/architecture-decision-records/ADR-001-runtime-choice.md`
- `docs/risk-register.md`
- `docs/test-results/phase-0.md`
- `docs/phase-0-closeout.md`
- `artifacts/doubao-audit-screenshots/`
- `artifacts/doubao-audit-logs/`

证据可能包含账号界面的低敏身份信息；仓库必须保持私有，提交前应检查截图并遮盖不必要的信息。

## Phase 1 输出

- `docs/phase-1-closeout.md`
- `docs/architecture.md`
- `docs/data-dictionary.md`
- `docs/security.md`
- `backend/architectpass_state/`
- `schemas/`
- `deployment/feishu/production-v1.json`
- `tests/unit/` and `tests/fixtures/phase1-feishu-canary-backup.json`
- `scripts/phase1_healthcheck.py`

Run `python3 scripts/phase1_healthcheck.py` for the local regression and captured-deployment checks. It intentionally reports live Feishu authentication as partial because credentials stay platform-managed.

Offline writes use `PersistentOfflineOutbox` in a caller-authorized existing local directory. The queue is checksum-protected, atomically persisted with mode `0600`, retains the original request/audit context across restart, and removes entries only after an acknowledged successful replay.

## Phase 2 输出

- `backend/architectpass_materials/`
- `schemas/material-manifest-v1.json`
- `schemas/video-progress-v1.json`
- `materials/manifests/`
- `deployment/models/local-processing-v1.json`
- `scripts/phase2_healthcheck.py`
- `docs/phase-2-closeout.md`
- `docs/test-results/phase-2.md`

Use the bundled project Python to run `scripts/phase2_healthcheck.py`. Raw course files, local models, generated audio/transcripts and private indexes are intentionally ignored and never part of the repository.

## Phase 3 输出

- `backend/architectpass_cheko/`
- `schemas/cheko-practice-v1.json`
- `deployment/cheko/ui-contract-v1.json`
- `scripts/phase3_healthcheck.py`
- `tests/fixtures/cheko-submitted-report-sanitized.json`
- `docs/phase-3-closeout.md`
- `docs/test-results/phase-3.md`

Run `python3 scripts/phase3_healthcheck.py` to verify the post-submission gate, forbidden actions/content, UI contract, fallbacks and Cheko tests. The adapter has no private network client and no answer/submit operation.

## Phase 4 输出

- `backend/architectpass_controller/`
- `schemas/learning-controller-v1.json`
- `scripts/phase4_healthcheck.py`
- `tests/unit/test_controller.py`
- `docs/phase-4-closeout.md`
- `docs/test-results/phase-4.md`

Run `python3 scripts/phase4_healthcheck.py` to verify the fixed lifecycle, state-read gate, dynamic review baseline, anti-answer/submit boundary, essay anti-fabrication guard and Phase 4 tests.

## Phase 5 输出

- `skills/doubao/`
- `deployment/doubao/`
- `deployment/doubao/bootstrap-v1.md`
- `scripts/build_doubao_skills.py`
- `scripts/render_doubao_system_instructions.py`
- `scripts/phase5_healthcheck.py`
- `docs/phase-5-closeout.md`
- `docs/test-results/phase-5.md`
- `artifacts/doubao-audit-logs/phase5-installation-2026-09-04.md`

Run `python3 scripts/phase5_healthcheck.py` to render the instruction baseline, rebuild deterministic private skill packages, enforce the minimum-permission manifest, and run Phase 5 package tests. Build archives and hashes are generated under ignored `dist/doubao-skills/`.

## Phase 6 输出

- `backend/architectpass_initialization/`
- `deployment/phase6/`
- `scripts/render_phase6_initialization.py`
- `scripts/build_phase6_private_segments.py`
- `scripts/phase6_healthcheck.py`
- `docs/phase-6-closeout.md`
- `docs/test-results/phase-6.md`
- `artifacts/doubao-audit-logs/phase6-initialization-2026-09-04.md`

Run `python3 scripts/phase6_healthcheck.py` to build the deterministic initialization plan and validate Phase 6. Private segment payloads are generated only under ignored `dist/`; course text is never a Git artifact. Prior exam attempts and scores are optional.
