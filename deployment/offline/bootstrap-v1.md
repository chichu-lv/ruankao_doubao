# 从压缩包安装

这份协议适用于已解压的 `ArchitectPass-offline` 目录，优先于 Git 安装协议中的取仓库、分支检查和百度网盘步骤。联网服务仍由当前用户自己的豆包、飞书和芝士架构账号提供。

先完整读取并执行 `project/deployment/doubao/execution-context-v1.md`（从 project 根目录读取时省略 project/）。当前执行者就是豆包，不是 Codex；先执行 `CONTEXT_CHECK`。不在虚拟桌面登录豆包，不启动第二个豆包。只有云电脑时报告 `NEEDS_LOCAL_MODE`，自身界面不可操作时报告 `NEEDS_USER_UI`，请求具体用户点击。

1. 读取包根的 `README-OFFLINE.md`、`offline-manifest.json`，以及 `project/` 内 README、01 产品说明、02 总执行指令、03 系统指令模板和04 验收清单。原产品背景不作为新用户档案，开发阶段审计无需重做。
2. 以包内 `project/` 为代码目录，`private-materials/` 为资料目录；校验目录和文件数量。包中没有 `.git` 是正常的，无需连接 GitHub 或百度网盘。
3. Windows 10/11 64 位建议解压至 `C:\AP` 等短路径，在 `project/` 中运行 `scripts\start_windows.cmd`；Apple 芯片 Mac 运行 `bash scripts/start_macos.sh`。二者自动使用包内 Python 和依赖，无需预装 Python、Git 或连接包源。使用 `dist/bootstrap/local-bootstrap-result.json` 判断本地安装；缺少 OCR/ASR 可用本地 PDF 阅读、页码和视频时间点继续学习。
4. Windows 运行 `.runtime\python\python.exe -X utf8 scripts\prepare_offline_materials.py`；Mac 运行 `.venv/bin/python3 scripts/prepare_offline_materials.py`。生成解压路径下的全量资料清单和首批 PDF 页级索引。后续使用 `--file "相对于 private-materials 的文件路径"` 增量索引所需 PDF，`--search "知识点"` 检索。运行结果会列出已索引与未索引范围，不能把目录登记当成全量全文转写。
5. 首次创建新的豆包私有项目 `架构上岸教练`（无关同名项目保留，新项目增加后缀）；恢复时先核对用户确认属于本次部署的项目，不重复创建。安装 `prebuilt-skills/` 中九个技能；若当前账号已存在同内容且启用的技能可复用。把 `project/deployment/doubao/system-instructions-v1.md` 绑定到项目，并告知代码与资料目录的实际位置。自身菜单不可操作时请用户完成具体创建/导入动作，不转用虚拟桌面。
6. 使用当前账号的飞书连接器，在用户选择的私人空间创建 `ArchitectPass State v1`，按 `schemas/feishu-bitable-v1.json` 建立 15 张表。已有 Base 时先确认是本次要继续使用的学习状态。测试安装使用另名 Base。把实际项目名称、Base 名称与标识、资料路径保存在 `dist/deployment/project-state.json`，并将此配置附入豆包项目上下文；后续始终使用该绑定。操作前必须阅读 `deployment/feishu/write-protocol-v1.md`，不能把回读解析失败当作零记录后重复新增。
7. 按飞书写入协议执行 `deployment/phase6/initialization-write-plan-v1.json` 的空档案和知识点初始化；已存在的用户画像原样保留。离线资源记录优先取 `materials/index/offline-inventory.json` 的本地路径，页级片段取 `materials/index/offline-catalog.json`。只有当前用户提供的学习结果才写入学习事件、掌握度和复习队列。完成后再做一次差异计算并回读计数，确认没有重复业务主键且不需要第二次新增。
8. 首次只补问影响当天计划的信息：考试日期、可用时间、已学范围；历史成绩可跳过。打开豆包浏览器中的芝士架构官方页面完成登录。按当前用户作息设定提醒；周六 20:00 是推荐值，不代表接收者已经确认。
9. 运行 `ruankao-healthcheck-v1`，实际读取新 Base，检索一条带页码的本地资料，再用“启动今日软考训练。我有 90 分钟，精力一般。”验证首次计划。在真实学习或明确标记的测试作答后，检查事件、复习和 checkpoint 写入与回读，再在新对话恢复。

## 豆包项目创建与本地电脑

运行前确保用户已在豆包完成所需“操作电脑”系统授权。桌面新工作任务页的「项目 → 创建新项目」是已实测入口。若当前豆包不能操作自身界面，报告 `NEEDS_USER_UI`，请用户在桌面完成具体点击后核对结果。禁止以豆包官方网页、虚拟桌面或再次登录豆包作为降级路径；不读写客户端内部存储来伪造项目。

网页新任务可能默认「云电脑」，不能读取本机离线包。项目创建后，回到桌面客户端并确认任务选择「本地电脑」，再读取代码、资料及当前 Base 绑定。没有持久指令字段时，仅在真实支持项目文件的入口绑定；若该入口也不存在，保留本机系统指令和配置，并交付带实际 project 路径的恢复提示词。新增同项目对话后实际读取文件并回读在线检查点，不能仅靠安装对话的记忆，也不能将首条消息称为项目级持久配置。豆包自身无法点击桌面模式时，用户只需在桌面新工作任务中选择「本地电脑」、选择项目并粘贴提示词。

本地脚本不携带飞书登录，所以本地检查的 live_feishu 项为 PARTIAL；只有豆包实际连接后，才能报告在线状态层通过。测试数据只能放入测试 Base。

日常入口：`启动今日软考训练。我有 90 分钟，精力一般。`

同一任务继续入口：`继续上次训练，先读取最近检查点。`

新任务恢复入口：`从【本机实际 project 路径】恢复架构上岸教练，先读取 deployment/doubao/system-instructions-v1.md 和 dist/deployment/project-state.json，再回读最近检查点继续训练。` 只有已验证项目级绑定在新会话生效，才可省略路径。

恢复入口：`检查并恢复软考系统，再从未完成事项继续。`
