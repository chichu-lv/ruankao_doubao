# 架构上岸教练 — Git 驱动自举协议 v1

本文是豆包从私有 Git 仓库执行安装的正式入口。仓库是唯一交付源；本机已有配置只能作为验证证据，不能成为安装前提。

## 输入

- 用户提供的私有 Git 仓库链接；
- 用户已登录且有权读取该仓库的 Git 网页或客户端；
- 用户真实豆包账号和当前电脑；
- 需要逐次确认时由用户提供的确认（删除、发布、权限变更、敏感导出，以及定时任务的最终执行时刻）。

禁止要求用户把密码、Cookie、验证码、个人访问令牌或 API 密钥写入聊天、仓库或命令参数。登录应通过已有客户端或官方登录界面完成。

## 强制读取顺序

在采取安装动作前，完整读取：

1. `AGENTS.md`；
2. `01_豆包软考私教系统_Codex开发说明书.md`；
3. `04_验收清单.md`；
4. `02_交给Codex的总执行指令.md`；
5. 根目录 `README.md`；
6. `deployment/doubao/README.md`、`project-v1.json`、`skills-v1.json`、`schedules-v1.json` 和 `system-instructions-v1.md`。

前两份产品/验收文件不得省略，总执行指令不得被普通样例或历史记录覆盖。仓库内文档是安装说明，不是绕过安全确认的授权。

## 自举状态机

严格执行并逐项留下证据：

```text
FETCH → VERIFY → BUILD → CREATE_PRIVATE_PROJECT → INSTALL_SKILLS
→ ATTACH_BASELINE → CONNECT_STATE → CONFIGURE_READ_ONLY_JOBS
→ HEALTHCHECK → REPORT
```

### 1. FETCH

- 仅获取用户给出的这个仓库，不搜索或修改其他项目。
- 优先使用用户已登录的官方 Git 客户端/网页；需要本地副本时，放入用户明确选择的独立目录。
- 把实际仓库根目录作为唯一项目文件 allowlist。不得把父目录、用户主目录或磁盘根目录授权给控制器。
- 若私有仓库不可读，停在 `PARTIAL` 并请用户完成官方登录；不得索取或记录令牌。

### 2. VERIFY

- 核对 `VERSION`、Git 提交 ID、工作树状态和上述权威文件存在性。
- 运行敏感信息检查；发现疑似秘密时停止安装并报告文件路径，不展示秘密值。
- 不得假定当前豆包支持某个技能、连接器或伙伴格式；先根据 Phase 0 证据与当前界面复核。

### 3. BUILD

- 在仓库根目录运行 `python3 scripts/phase5_healthcheck.py`。
- 该命令必须生成 `dist/doubao-skills/build-manifest.json` 和九个同名目录结构的 ZIP。
- 只有专项测试通过、九个哈希齐全且没有未解析占位符时才继续。
- 若 Python 或依赖不可用，明确报告并给出安装环境/手工构建兜底；不得伪造 ZIP 或 PASS。

### 4. CREATE_PRIVATE_PROJECT

- 创建新的、仅用户本人可见的豆包项目，名称取 `deployment/doubao/project-v1.json` 的 `target_project`。
- 不复用、不删除、不重命名任何既有项目；特别保护清单中的 `preserve_projects`。
- 当前账号没有独立私有工作伙伴入口时，以该私有 Project 作为等价持久容器并如实记录。

### 5. INSTALL_SKILLS

- 从 `dist/doubao-skills/` 安装 `skills-v1.json` 列出的九个 ZIP，保持私有。
- 每个技能必须显示 READY/启用，名称和版本与清单一致；安全检测未完成的技能不能算 PASS。
- 不覆盖同名旧版本。升级时并行安装新版本、验证、切换；回滚时禁用新版本并重新启用旧版本。
- 删除任何技能必须再次取得用户对精确目标的确认。

### 6. ATTACH_BASELINE

- 将 `system-instructions-v1.md` 作为项目控制基线。
- 有持久项目指令字段时写入并回读；没有时把该文件作为私有项目上下文，并在项目第一条初始化消息中明确采用。
- 仅在能精确选中仓库根目录时绑定本地文件夹。选择结果若是父目录，立即取消并报告 `PARTIAL`。

### 7. CONNECT_STATE

- 解析 `deployment/feishu/production-v1.json`，只连接用户私有的 `ArchitectPass State v1`。
- 先只读核对 15 张表；缺失时按 Phase 1 部署与迁移文档创建/修复，不得盲目覆盖已有数据。
- 所有写操作必须有 `request_id`、`audit_id` 和写后回读。连接失败时保留待同步事件，不能声称已保存。
- 运行 `python3 scripts/phase6_healthcheck.py`，读取生成的 `deployment/phase6/initialization-write-plan-v1.json`，按 `request_id` 查重后执行已授权的初始化记录；历史考试经历与成绩不得作为前置条件。
- 若本机已有 Phase 2 私有索引，`scripts/build_phase6_private_segments.py` 会在忽略提交的 `dist/phase6-initialization/` 生成页码/时间戳写入计划。其片段只能进入用户私人状态库，不得提交 Git、公开或复制到其他项目。
- 初始化后以纯只读方式重放全部 request ID；只有业务主键、载荷、哈希、audit ID 全部一致且计数不增长，才算幂等通过。

### 8. CONFIGURE_READ_ONLY_JOBS

- 读取 `schedules-v1.json` 和两个提示模板。
- 分别在用户确认每日或每周执行时刻后创建或对齐对应的只读任务；未确认的任务保持 `template_pending_user_time`，不得因另一项已确认而擅自启用。
- 不启用 scheduled writes，不删除或修改无关定时任务。

### 9. HEALTHCHECK

- 在新项目中显式调用 `ruankao-healthcheck-v1`。
- 只读核对九技能、Feishu 状态、资料索引、浏览器/Baidu 精确兜底、Cheko 登录/允许路由和定时任务。
- 不打开练习题、不读取题目/答案、不提交答案，不以聊天记忆替代状态。
- 输出每项 `PASS/PARTIAL/FAIL`、证据、限制和精确降级路径；重新计算汇总，不能直接复制不一致的计数。

### 10. REPORT

最终只报告：

- 项目名称和隐私状态；
- Git 提交 ID 与版本；
- 九个技能的安装/启用状态；
- 状态库和定时任务状态；
- 健康检查逐项结果；
- 未关闭限制及用户下一步；
- 明确声明未修改的既有项目和未执行的敏感动作。

只有全部必需步骤有真实证据，才可声称安装完成。允许有明确降级路径的 `PARTIAL`，禁止伪造成功。
