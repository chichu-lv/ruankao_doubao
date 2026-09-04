---
name: ruankao-healthcheck-v1
description: 架构上岸教练部署与恢复健康检查。首次启动、每日启动前、工具失败、升级后或用户说“检查并恢复软考系统”时使用。检查技能、飞书状态、资料索引、芝士架构、浏览器和定时任务，输出 PASS/PARTIAL/FAIL 与降级路径；禁止假装成功。
---

# Ruankao Healthcheck v1

## 检查顺序

1. 九个 `*-v1` 私有技能是否可见并启用。
2. 私人飞书 Base `ArchitectPass State v1` 是否可读；仅回读无敏感 canary，不写入。
3. 本地材料清单/索引是否可读，引用是否含页码或原视频时间戳。
4. 芝士架构登录与允许路由是否可见；不开始练习、不读题目答案。
5. 豆包浏览器、百度网盘人工定位路径是否可用。
6. 每日/周报定时任务是否启用且保持只读。
7. 最近 checkpoint、备份清单和待同步队列是否一致。

## 结果

每项只能为：

- `PASS`：有本次可见/回读证据；
- `PARTIAL`：主路径不可用但明确降级可继续；
- `FAIL`：无安全可用路径。

输出 `component/status/evidence/limitation/fallback/next_action`。整体状态取最差项；状态写入失败不能报告 PASS。

## 恢复

从最近一次成功 checkpoint 继续，列出可自动修复项和需确认项。断网时保留待同步事件但不声称写入；技能失效时指明精确技能名与版本。

## 输出与错误

统一返回 `status/data/error/audit_id`。错误包括 `STATE_READ_FAILED`、`SKILL_MISSING`、`INDEX_UNAVAILABLE`、`CHECKPOINT_UNAVAILABLE` 和 `MANUAL_FALLBACK_REQUIRED`。

## 安全边界

健康检查只读。不删除、不发布、不付款、不改权限、不批量覆盖、不导出敏感数据；不记录密码、Cookie、验证码、密钥或完整课程/题库正文。
