# ArchitectPass / 架构上岸教练

这是供豆包从 Git 自动部署的正式交付分支。日常学习主控固定为豆包；芝士架构继续负责做题，百度网盘继续提供用户有权使用的资料，长期状态保存在用户私有的飞书多维表格中。

收到压缩包的新用户：先解压，再执行包根的 `README-OFFLINE.md` 和 `deployment/offline/bootstrap-v1.md`；该路径不需要 Git 仓库或百度网盘。首次档案为空，资料索引用 `scripts/prepare_offline_materials.py` 在当前电脑建立。原始基线中的个人经历不是接收者的学习数据。

## 豆包一键初始化

Git 仓库：

```text
https://github.com/chichu-lv/ruankao_doubao.git
```

在豆包桌面客户端新建工作任务，确认选择「本地电脑」，再发送上面的链接和下面整段提示词。网页版的「云电脑」不能读取本机资料包。首次账号登录和系统权限弹窗仍需本人完成，后续由豆包执行部署：

```text
请从私有 Git 仓库 https://github.com/chichu-lv/ruankao_doubao.git 的 main 分支部署“架构上岸教练”。完整读取根目录 README.md，并执行 deployment/doubao/bootstrap-v1.md。使用本地电脑，在全新的豆包项目中完成九个私有技能安装、系统指令绑定和我的空档案建档；通过我已登录的百度网盘官方界面，仅连接“00、【推荐】【26年10月】wen老师架构课程（第二版）”和“5、【2026年05月】芝士架构系统架构设计师”两个授权目录，按需建立本机索引；连接我自己的飞书状态层，按我确认的时间配置复盘提醒，并执行健康检查。不要把课程原文件、转写正文或私有索引提交到 Git。安装所需项目内操作已授权；需要登录时让我在官方界面完成。完成后开始今日训练。
```

## 豆包必须执行的入口

[deployment/doubao/bootstrap-v1.md](deployment/doubao/bootstrap-v1.md) 是唯一安装状态机。豆包必须从当前克隆目录解析仓库根路径，不得使用开发电脑的历史绝对路径，也不得把父目录、用户主目录或磁盘根目录加入权限范围。

正式安装会：

1. 校验 `main`、`VERSION`、必需文件和敏感信息边界；
2. Windows 先运行 `scripts/download_windows_runtime.ps1` 获取项目私有环境，再运行 `scripts\start_windows.cmd`；Mac/Linux 运行 `python3 scripts/bootstrap_local.py`。安装依赖并构建九个私有豆包技能包；完整离线包不需要下载运行环境；
3. 新建私有项目 `架构上岸教练`，不复用或修改已有项目；
4. 绑定 `deployment/doubao/system-instructions-v1.md`；
5. 按 `schemas/feishu-bitable-v1.json` 连接或初始化私有 `ArchitectPass State v1`；
6. 通过已登录的百度网盘官方界面，仅核对两个授权课程目录，并按学习需要增量建立本机私有索引；
7. 幂等核对初始化数据，保留本地资料和芝士架构的安全边界；
8. 按当前用户作息配置只读提醒，周六 20:00 可作为推荐时间；
9. 调用 `ruankao-healthcheck-v1` 并按 `PASS/PARTIAL/FAIL` 如实报告。

## 交付内容

- `skills/doubao/`：九个版本化私有技能；
- `deployment/doubao/`：豆包项目、自举、系统指令和只读任务配置；
- `deployment/feishu/` 与 `schemas/`：私有状态层定位和数据契约；
- `backend/`：状态、资料、芝士结果、学习控制与初始化逻辑；
- `materials/manifests/`：用户已授权资料的私有清单；
- `scripts/`：构建、初始化与健康检查入口；
- `tests/`：部署前本地安全和回归检查。
- `deployment/offline/`：GitHub 或百度网盘不可访问时的私有离线压缩包方案。

产品和验收基线 `01_豆包软考私教系统_Codex开发说明书.md`、`02_交给Codex的总执行指令.md`、`03_豆包工作伙伴_最终系统指令模板.md`、`04_验收清单.md` 必须保留并在自举时读取。开发过程、审计截图、阶段日志和历史测试报告仅保存在 `development` 分支，不属于正式部署输入。

## 更新与维护

同一任务中可以直接说「继续上次训练」。换新任务时仍需选择「本地电脑」；如果当前豆包没有项目级文件/指令绑定入口，请使用：

```text
从【实际解压或克隆目录中的 project 路径；Git 安装用仓库根目录】恢复架构上岸教练，先读取 deployment/doubao/system-instructions-v1.md 和 dist/deployment/project-state.json，再回读最近检查点继续训练。
```

目录是新会话找到本机持久配置的入口，不需要重复提供飞书标识、历史成绩或学习进度。只在已验证新会话能自动找到绑定文件时，才可以省略目录。

正式版本见 `VERSION`。更新时重新拉取 `main`，按 `deployment/update/README.md` 执行；任何删除、发布、权限变化、批量覆盖或敏感数据导出仍需用户对精确目标单独确认。

需要提前制作离线备份时，先把两个授权百度网盘目录通过官方界面下载到同一父目录，再按 `deployment/offline/README.md` 生成不进入 Git 的私有 ZIP。压缩包内置正式项目快照、九个预构建技能包和实际纳入的资料清单；缺文件时只能生成明确标注的 `PARTIAL` 包。
