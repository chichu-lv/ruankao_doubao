# 新用户干净沙盒验收 — 2026-09-04

## 结论

整体结果：`FAIL`（针对“新用户仅给 Git 链接和提示词即可无人值守完成全部搭建”这一目标）。

在完成 GitHub 授权并人工选择可用 Python 3.12 后，核心本地构建、九技能安装模拟、初始化、首次训练、checkpoint 和离线恢复均通过。但默认运行时发现和跨克隆可复现构建存在缺陷；真实豆包、百度网盘、飞书与定时任务界面不在沙盒内，不能伪报已完成。

被测发布：

- 仓库：`https://github.com/chichu-lv/ruankao_doubao.git`
- 分支：`main`
- 提交：`56949d46d97b409fd50bdd812272c30fd9175468`
- 版本：`1.0.1`

## 隔离条件

- 使用两个全新的临时目录分别克隆远端 `main`；
- 不读取开发工作区的 `dist/`、`materials/index/`、模型、转写或其他忽略文件；
- 第一条路径严格使用 README 中的 HTTPS URL，并禁用交互式凭据询问；
- 外部账号连接只按沙盒真实可用性报告，不使用伪造 Token、Cookie 或假成功响应。

## 结果矩阵

| 项目 | 结果 | 证据/说明 |
|---|---|---|
| 未登录用户仅凭私有 HTTPS 链接克隆 | `EXPECTED_BLOCK` | Git 返回 `could not read Username`；私有仓库必须先通过官方 GitHub 登录/授权。 |
| 使用本机已授权 GitHub 身份克隆 | `PASS` | 得到干净 `main`，提交和版本与上方一致，发布历史 2 个提交。 |
| README 默认构建命令 | `FAIL` | 系统 `python3` 为 3.9.6；`python3 scripts/phase5_healthcheck.py` 直接返回需要 Python 3.11+。提示词没有自动发现/创建兼容运行时。 |
| 使用已存在 Python 3.12 构建 | `PASS` | 九个技能 ZIP 和 manifest 成功生成，专项测试通过。 |
| 九技能安装模拟 | `PASS` | 九个 ZIP 解压为九个同名顶层目录，每个包含 `SKILL.md`；系统指令文件成功绑定到隔离项目上下文。 |
| 跨独立克隆的技能包哈希 | `FAIL` | 两次全新克隆的 9/9 ZIP SHA-256 均不相同。构建脚本使用源文件时间戳写 ZIP，与“可复现包”声明不一致。 |
| Phase 1 状态契约 | `PASS/PARTIAL` | 15 表映射与单测通过；实时飞书认证按实报告 `PARTIAL`。 |
| Phase 2 私有资料 | `FAIL/PARTIAL` | 二进制和资料授权清单通过；两个本地 OCR/ASR 模型缺失。脚本返回 FAIL，但自举协议规定这种情况应为 PARTIAL 并采用官方界面人工页码/时间点兜底。 |
| Phase 3 芝士边界 | `PASS` | 13 项测试通过；自动选答、提交与提交前答案读取均不在允许操作中。 |
| Phase 4 学习控制器 | `PASS` | 28 项控制器/状态测试通过。 |
| Phase 6 初始化 | `PASS/PARTIAL` | 15 条公开初始化操作通过且可幂等重放；Git 不含私有页码/时间戳目录，2 项私有索引测试按设计跳过。 |
| 全量单元回归 | `PASS` | 85 项执行完成，83 通过，2 项按设计跳过。 |
| 首次用户训练 | `PASS` | 创建 30 分钟会话，生成 25 分钟计划，进入 `AWAITING_HUMAN`，只在模拟用户提交可追溯输出后继续，最终 `FINISHED` 并保存 checkpoint。 |
| 状态写审计 | `PASS` | 初始化和首次训练共生成 24 条审计记录；初始化 request ID 重放全部去重。 |
| 芝士自动答题阻断 | `PASS` | 调用 `select_answer` 返回 `OPERATION_NOT_ALLOWED`。 |
| 飞书断线恢复 | `PASS` | 持久离线 outbox 在重新实例化后仍保留待同步写入，仅在模拟成功确认后清除。 |
| 百度网盘真实目录连接 | `NOT_TESTABLE_IN_SANDBOX` | 沙盒无用户百度登录会话；仅验证两个精确授权根、禁止整库下载和本机私有索引策略。 |
| 真实豆包项目创建/技能导入 | `NOT_TESTABLE_IN_SANDBOX` | 用隔离目录模拟产物安装，不能替代豆包真实 UI 的 READY/启用证据。 |
| 飞书真实 Base 写后回读 | `NOT_TESTABLE_IN_SANDBOX` | 无真实飞书授权；使用非权威内存适配器和持久离线 outbox 验证降级路径。 |
| 每周六 20:00 真实任务 | `NOT_TESTABLE_IN_SANDBOX` | 配置解析正确，未在用户真实账号创建或修改任务。 |

## 首次使用输出摘要

```json
{
  "version": "1.0.1",
  "skills_installed": 9,
  "authorized_material_roots": 2,
  "initialization_operations": 15,
  "initialization_idempotent_replay": true,
  "plan_minutes": 25,
  "waited_for_human": true,
  "session_status": "FINISHED",
  "checkpoint_saved": true,
  "automatic_cheko_answer_blocked": true,
  "audit_records": 24
}
```

## 必须修复后再判定“一键可用”的项目

1. 增加单一自举入口，自动发现 Python 3.11+；存在 `uv` 时自动创建私有 `.venv` 并安装锁定依赖，否则输出一个明确、可执行的用户动作。README 不应直接假设 `python3` 合格。
2. 固定 ZIP 条目的时间戳、权限和排序，使不同克隆对同一提交生成完全相同的 SHA-256。
3. 统一 Phase 2 状态语义：本地 OCR/ASR 模型缺失应按协议返回 `PARTIAL`，并明确哪些资料能力仍可通过官方界面工作。
4. 修复后重新做本报告的两个全新克隆测试，再进入真实豆包账号的一次空项目安装验收。

在上述前三项修复且真实外部界面验收完成前，不得声称“仅链接和提示词即可完成全部搭建”。
