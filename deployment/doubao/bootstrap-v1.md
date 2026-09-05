# 架构上岸教练 — Git 驱动自举协议 v1

本文是豆包从私有 Git 仓库执行安装的正式入口。仓库是唯一交付源；本机已有配置只能作为验证证据，不能成为安装前提。

## 离线包与新用户

如果项目的父目录包含 `offline-manifest.json`，改为执行 `deployment/offline/bootstrap-v1.md`。该模式使用包内项目和资料，无需 `.git`、Git 分支或百度网盘登录；不得执行下文 FETCH/Git 校验步骤。

本文及离线安装协议是原始产品基线面向新用户的实现补充。基线中“两次考试、视频已看一半”等是原用户背景，不是接收者的事实。初始化仅创建空档案、知识点和资料元数据，保留已存在的档案；考试日期、进度、成绩和作息均由当前用户提供。测试夹具只能用于测试。

## 输入

- 用户提供的私有 Git 仓库链接；
- 用户已登录且有权读取该仓库的 Git 网页或客户端；
- 用户真实豆包账号和当前电脑；
- 需要逐次确认时由用户提供的确认（删除、发布、权限变更、敏感导出，以及定时任务的最终执行时刻）。

禁止要求用户把密码、Cookie、验证码、个人访问令牌或 API 密钥写入聊天、仓库或命令参数。登录应通过已有客户端或官方登录界面完成。

## 强制读取顺序

在采取安装动作前，完整读取：

1. 根目录 `README.md`；
2. `01_豆包软考私教系统_Codex开发说明书.md`；
3. `04_验收清单.md`；
4. `02_交给Codex的总执行指令.md`；
5. `03_豆包工作伙伴_最终系统指令模板.md`；
6. `deployment/doubao/README.md`、`project-v1.json`、`skills-v1.json`、`schedules-v1.json` 和 `system-instructions-v1.md`。

前两份产品/验收文件不得省略，总执行指令不得被普通样例或历史记录覆盖。仓库内文档是安装说明，不是绕过安全确认的授权。

## 自举状态机

严格执行并逐项留下证据：

```text
FETCH → VERIFY → BUILD → CREATE_PRIVATE_PROJECT → INSTALL_SKILLS
→ ATTACH_BASELINE → CONNECT_PRIVATE_MATERIALS → CONNECT_STATE → CONFIGURE_READ_ONLY_JOBS
→ HEALTHCHECK → REPORT
```

### 1. FETCH

- 仅获取用户给出的这个仓库，不搜索或修改其他项目。
- 必须使用 `main` 分支；若当前不是 `main` 或工作树包含非仓库改动，停止并如实报告。
- 优先使用用户已登录的官方 Git 客户端/网页；需要本地副本时，放入用户明确选择的独立目录。
- 把实际仓库根目录作为唯一项目文件 allowlist。不得把父目录、用户主目录或磁盘根目录授权给控制器。
- 若私有仓库不可读，停在 `PARTIAL` 并请用户完成官方登录；不得索取或记录令牌。

### 2. VERIFY

- 核对 `VERSION` 与 `pyproject.toml` 一致、`main` 分支、Git 提交 ID、工作树状态和上述权威文件存在性。
- 运行敏感信息检查；发现疑似秘密时停止安装并报告文件路径，不展示秘密值。
- 不得仅凭清单假定当前豆包仍支持某个技能、连接器或项目格式；先在当前真实账号与界面只读复核。若界面变化，使用手工导入/私有项目上下文等已写明的降级路径，不得猜测成功。

### 3. BUILD

- Windows 10/11 x64：在仓库根目录先运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/download_windows_runtime.ps1`，从 Python 官方与 PyPI 获取项目私有运行环境，再运行 `scripts\start_windows.cmd`；无需先安装系统 Python、pip 或 uv。需要能访问上述官方源；已有完整离线包时跳过下载。PowerShell 参数只用于这一次脚本进程，不修改系统执行策略。
- Mac/Linux：在仓库根目录运行 `python3 scripts/bootstrap_local.py`。此入口保持兼容系统 Python 3.9，并自动发现 Python 3.11+；没有兼容解释器但已有 `uv` 时，只在仓库私有 `.runtime/` 和 `.venv/` 中配置 Python 3.12 与依赖。
- 该命令必须生成 `dist/bootstrap/local-bootstrap-result.json`、`dist/doubao-skills/build-manifest.json` 和九个同名目录结构的 ZIP。
- 只有专项测试通过、九个哈希齐全且没有未解析占位符时才继续。
- 非 Windows 路径若既没有 Python 3.11+ 也没有 `uv`，明确报告一个通过官方来源安装 Python 3.12 或 `uv` 的用户动作；不得修改系统 Python，不得伪造 ZIP 或 PASS。
- `phase2_healthcheck.py` 的 `PARTIAL` 表示本地 OCR/ASR 能力不完整但官方界面人工页码/时间点兜底仍可用，不得把该状态改写为 PASS。

### 4. CREATE_PRIVATE_PROJECT

- 创建新的、仅用户本人可见的豆包项目，名称取 `deployment/doubao/project-v1.json` 的 `target_project`。
- 不复用、不删除、不重命名任何既有项目；特别保护清单中的 `preserve_projects`。
- 当前账号没有独立私有工作伙伴入口时，以该私有 Project 作为等价持久容器并如实记录。
- 已实测入口为新工作任务页的「项目 → 创建新项目」。桌面辅助功能仅显示菜单栏时，可通过同账号豆包官方网页创建，并在桌面侧边栏回读验证同步；不使用客户端内部存储伪造项目。网页默认云电脑不等于本地电脑，读取本机仓库和资料前必须在桌面任务确认选择「本地电脑」。

### 5. INSTALL_SKILLS

- 从 `dist/doubao-skills/` 安装 `skills-v1.json` 列出的九个 ZIP，保持私有。
- 每个技能必须显示 READY/启用，名称和版本与清单一致；安全检测未完成的技能不能算 PASS。
- 不覆盖同名旧版本。升级时并行安装新版本、验证、切换；回滚时禁用新版本并重新启用旧版本。
- 删除任何技能必须再次取得用户对精确目标的确认。

### 6. ATTACH_BASELINE

- 将 `system-instructions-v1.md` 作为项目控制基线。
- 有持久项目指令字段时写入并回读；没有时仅在真实支持附加私有项目文件的入口绑定。若两者都没有，把系统指令和当前 Base 配置保存在本机，并交付带项目路径的恢复提示词；不得把首条聊天说明称为项目级持久绑定。
- 新会话必须实际读取上述文件并回读在线检查点。桌面选择「本地电脑」无法由豆包自身操作时，说明最短补充动作「桌面新工作任务 → 本地电脑 → 选择项目 → 粘贴恢复提示词」，记录为用户辅助路径，不宣称完全无人操作。
- 仅在能精确选中仓库根目录时绑定本地文件夹。选择结果若是父目录，立即取消并报告 `PARTIAL`。

### 7. CONNECT_PRIVATE_MATERIALS

- 读取 `project-v1.json` 的 `materials.authorized_baidu_scopes` 和 `materials/manifests/authorized-sources-v1.json`；只允许以下两个精确目录：
  - `00、【推荐】【26年10月】wen老师架构课程（第二版）`
  - `5、【2026年05月】芝士架构系统架构设计师`
- 使用用户当前已登录的百度网盘官方网页或客户端核对目录。未登录时暂停，让用户在官方界面完成登录；不得索取密码、Cookie、验证码或令牌。
- Git 只保存授权范围、文件元数据和索引程序，不保存课程原文件、课程正文、完整转写或私有检索索引。运行时数据仅写入被 `.gitignore` 排除的 `materials/inbox/`、`materials/index/`、`materials/parsed/` 和 `materials/models/`，或用户另行明确授权的本机目录。
- 不做两个目录的整库下载。先核对远端清单；开始某个学习单元时，才通过官方界面获取所需 PDF、视频或字幕，并按文件哈希增量处理。不得绕过网盘会员、下载、播放、DRM 或分享限制。
- PDF 索引必须保留文件名和页码；视频转写必须保留原视频开始/结束时间与置信度。观看记录只能写成 `played_unchecked`，不能直接提升掌握度。
- 本机具备 Python 3.11+、`pdfplumber` 及 `deployment/models/local-processing-v1.json` 声明的本地处理工具后，运行 `python3 scripts/phase2_healthcheck.py`。缺少模型或工具时报告 `PARTIAL` 并继续使用“官方界面打开 + 人工页码/时间点”兜底，不得假装已建立全文索引。
- 每次新增或变化仅处理差异，输出保持私有；写入资源与学习进度时必须带唯一 `request_id`、`audit_id` 并回读验证。

### 8. CONNECT_STATE

- 解析 `deployment/feishu/production-v1.json`，只在用户已授权的飞书账号中按精确名称和 15 表 schema 定位私有 `ArchitectPass State v1`。发布分支不保存 Base URL、对象 ID 或表 ID。
- 先只读核对 `schemas/feishu-bitable-v1.json` 规定的 15 张表。零匹配时，在用户确认私有目标后按 schema/migration 创建；多匹配时必须让用户选择，禁止按内部 ID 猜测。缺失字段只按迁移链修复，不得盲目覆盖已有数据。
- 先阅读 `deployment/feishu/write-protocol-v1.md`。保存当前项目实际 Base 绑定到 `dist/deployment/project-state.json` 并附入项目上下文；所有写操作必须有稳定 `request_id`、`audit_id` 和写后回读。列表解析失败不是空表，不得盲目重试新增。连接失败时保留待同步事件，不能声称已保存。
- 运行 `python3 scripts/phase6_healthcheck.py`，读取生成的 `deployment/phase6/initialization-write-plan-v1.json`，按 `request_id` 查重后执行初始化记录；已有用户档案保持原值，不用模板覆盖。新账号学习事件、观看进度、掌握度和复习队列从空开始；历史考试经历与成绩不得作为前置条件。
- 若本机已有 Phase 2 私有索引，`scripts/build_phase6_private_segments.py` 会在忽略提交的 `dist/phase6-initialization/` 生成页码/时间戳写入计划。其片段只能进入用户私人状态库，不得提交 Git、公开或复制到其他项目。
- 初始化后以纯只读方式重放全部 request ID；只有业务主键、载荷、哈希、audit ID 全部一致且计数不增长，才算幂等通过。

### 9. CONFIGURE_READ_ONLY_JOBS

- 读取 `schedules-v1.json` 和两个提示模板。
- 分别在用户确认每日或每周执行时刻后创建或对齐对应的只读任务；未确认的任务保持 `template_pending_user_time`，不得因另一项已确认而擅自启用。
- 不启用 scheduled writes，不删除或修改无关定时任务。

### 10. HEALTHCHECK

- 在新项目中显式调用 `ruankao-healthcheck-v1`。
- 只读核对九技能、Feishu 状态、两个授权百度网盘目录、资料索引、浏览器/Baidu 精确兜底、Cheko 登录/允许路由和定时任务。
- 不打开练习题、不读取题目/答案、不提交答案，不以聊天记忆替代状态。
- 输出每项 `PASS/PARTIAL/FAIL`、证据、限制和精确降级路径；重新计算汇总，不能直接复制不一致的计数。

### 11. REPORT

最终只报告：

- 项目名称和隐私状态；
- Git 提交 ID 与版本；
- 九个技能的安装/启用状态；
- 状态库和定时任务状态；
- 两个百度网盘授权目录的连接状态、清单核对结果、已索引范围和未索引范围；
- 健康检查逐项结果；
- 未关闭限制及用户下一步；
- 明确声明未修改的既有项目和未执行的敏感动作。
- 不复述 Codex 开发过程，不读取或依赖 `development` 分支的审计历史。

只有全部必需步骤有真实证据，才可声称安装完成。允许有明确降级路径的 `PARTIAL`，禁止伪造成功。
