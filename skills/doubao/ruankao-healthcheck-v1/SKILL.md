---
name: ruankao-healthcheck-v1
description: 架构上岸教练部署与恢复健康检查。首次启动、每日启动前、工具失败、升级后或用户说“检查并恢复软考系统”时使用。检查技能、飞书状态、资料索引、芝士架构、浏览器和定时任务，输出 PASS/PARTIAL/FAIL 与降级路径；禁止假装成功。
---

# Ruankao Healthcheck v1

## 检查顺序

首先读取当前项目 `dist/deployment/project-state.json`，采用其 `state_base` 与本地资料路径。下述 Base 名只是默认值；不得离开当前测试/正式项目的绑定。压缩包模式无需检查 GitHub 或百度网盘，直接检查已解压资料。

1. 九个 `*-v1` 私有技能是否可见并启用。
   官方文件夹安装时，检查实际技能发现清单、调用及各自 `references/installation.json` 的同一根目录绑定；文件存在不等于发现通过，也不等于账号云端安装。原生侧边栏项目、私有本机工作区和文件夹技能分别报告，不因缺少原生指令字段就要求用户找不存在的入口。
2. 私人飞书 Base `ArchitectPass State v1` 是否可读；仅回读无敏感 canary，不写入。
3. 本地材料清单/索引是否可读，引用是否含页码或原视频时间戳。
4. 芝士架构登录与允许路由是否可见；不开始练习、不读题目答案。
5. Git/网盘安装时检查豆包浏览器、百度网盘人工定位路径；完整离线包已有资料时，此网盘登录项标为不适用，不因未登录网盘降低离线安装状态。
6. 只检查当前项目绑定的每日/周报任务，按任务 ID 或目标 Base 归属判断，不把账号下其他项目的提醒计入本项目。`reminders.enabled=false` 且本次未创建提醒是正常配置，不因发现既有无关提醒而报告冲突或建议停用。
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
