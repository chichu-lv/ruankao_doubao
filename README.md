# ArchitectPass / 架构上岸教练

一个由 Codex 开发和部署、以豆包工作私有工作伙伴为最终主控的“系统架构设计师”备考系统。

## 当前阶段

`Phase 2 — 资料导入与可追溯检索：已完成（含已记录限制）`

真实账号审计、Phase 1 状态层和 Phase 2 本地资料管线已经完成。私有飞书多维表格 `ArchitectPass State v1` 是权威结构化状态层；PDF、视频、字幕和索引保留在本地私有目录。资料管线提供哈希去重、页级/OCR 处理、本地时间戳转写、来源定位、进度导入、审计回执和健康检查。

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
