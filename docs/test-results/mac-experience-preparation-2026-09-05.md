# 开发产物整理与 Mac 正式体验准备

日期：2026-09-05。源码：1.1.3 / main 939c4bf。状态：本地运行环境 PASS；GUI 进入体验待用户解锁 Mac。

## 整理

用户授权整理开发过程产物，允许删除不必要内容。仅将确认过期的三个离线包移到用户废纸篓的 ArchitectPass-dev-cleanup-20260905 子目录：1.1.0-PARTIAL、1.1.0、早期 1.1.1，合计 54,047,537,109 字节。

将旧验收解压副本的 dist 输出与 offline-manifest 复制到项目 dist/qa/archived-doubao-acceptance-0905 后，把该旧副本也移入同一废纸篓，保留可恢复性。没有清空废纸篓，不宣称已释放对应空间。

development 工作树由 /private/tmp/architectpass-final.Yl56jH/development 用 git worktree move 迁到项目 dist/development-history，Git 工作树记录已更新。保留唯一最终交付包 dist/delivery/final/architectpass-offline-1.1.1.zip、Downloads 课程原文件、全部正式源码/运行环境/索引/模型、验收记录及远端学习状态。未删除豆包项目、飞书库、技能、提醒或 Git 分支。

本地用户导航文件：dist/本机体验与产物导航.md，区分正式使用与验收项目，并提供带稳定本机代码/资料路径的启动提示词。

## 本机启动缺陷与修复

真实运行 bash scripts/start_macos.sh，第一次失败：现有 .venv 由 uv 创建，没有 pip，而离线安装流程直接调用 python -m pip。不是 PDF 依赖缺失，也不需要改系统 Python。

增加 ensure_private_pip：只在项目解释器缺少 pip 时使用本地 ensurepip 引导；失败如实报告。Windows 嵌入式环境仍直接部署 wheel，不经过该分支。新增回归覆盖 pip 已存在、缺失时补齐、补齐失败三个情况。

修复后实际重跑成功：Python 3.12.13、existing_project_venv、bundled_wheels；六项本地 healthcheck 退出码均 0。Phase 2/3/4/5/6 PASS，Phase 1 为 live_feishu 尚待豆包在线回读的明确 PARTIAL。完整 99 项 unittest 全部通过；未修改系统 Python。

## GUI 与体验边界

已通过真实桌面界面打开现有正式「架构上岸教练」项目中的「架构上岸教练项目初始化与健康检查」对话，确认是本机 Mac 的本地电脑模式，而非 Acceptance 测试项目。

随后准备新建正式体验任务时 Mac 锁屏，工具明确无法操作。已请求用户手动解锁；没有绕过锁屏、自动答题或向正式库写入模拟数据。尚未发送正式体验启动消息，不能宣称用户已进入第一项训练。后续应新建同正式项目的本地任务，采用稳定项目根目录和 Downloads 两授权目录，回读正式状态后询问当天时间/精力，由用户本人开始学习。

本次未处理 Gitee 安装源适配（上一轮已报告其仍依赖 GitHub）；也未重建 1.1.1 完整资料包。
