# ArchitectPass / 架构上岸教练

一个由 Codex 开发和部署、以豆包工作私有工作伙伴为最终主控的“系统架构设计师”备考系统。

## 当前阶段

`Phase 1 — 仓库、数据模型与状态服务：已完成（含已记录限制）`

真实账号审计与 Phase 1 状态层已经完成。私有飞书多维表格 `ArchitectPass State v1` 是权威结构化状态层；本地代码提供受限状态契约、可重算掌握度、审计、备份/恢复、迁移、离线重放和健康检查。Phase 2 将处理增量资料导入与可追溯检索。

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
