# 最终交付验收：Windows 新用户

日期：2026-09-05（Asia/Shanghai）。状态：**有条件放行 / PASS_WITH_LIMITATIONS**。核心路径与最终包完整性校验均已通过；下述未覆盖项不得对外宣称通过。

本次是 Windows 本地运行环境实测、Mac 上真实豆包隔离项目/飞书状态库测试，以及七个逻辑日加速模拟。不是全新注册账号测试，不是 Windows 豆包 GUI 全流程，也不是实际七天独立运行。安装有人工等价客户端点击辅助及故障指导，不能称为完全无人干预安装。

## 来源与权限

- main：`567e3b8`，版本 `1.1.1`。正式分支只保留产品交付输入，开发报告在 development。
- Windows 通过的核心执行代码：`2a28bd6`；之后仅调整 CI 权限、入口说明、健康检查范围及文本契约断言，Windows 启动/运行代码未改变。
- 用户授权的临时 `contents: write` 仅用于 `codex/windows-acceptance` 日志分支。Windows 成功后已在 `3988fe1` 恢复 `contents: read`，删除写分支步骤并推送；后续只上传测试 artifact。没有修改仓库全局 Actions 默认权限设置。
- 成功运行：[33942450273](https://github.com/chichu-lv/ruankao_doubao/actions/runs/33942450273)，日志提交 `ffd77ce`，安装/单测/干净安装三步骤均 success。
- 最终交付包：`dist/delivery/final/architectpass-offline-1.1.1.zip`，26,710,010,690 字节（约 26.71 GB）。实际 ZIP 校验 PASS：349 文件无缺失、九技能 ZIP 可读、Windows runtime 与 8 wheel 在位、源码逐文件与 main 一致、无重复成员、无独立 SHA 文件、无测试用户状态、CI 只读。最长成员相对路径 151 字符。旧 `dist/offline/` 和 `dist/delivery/` 根目录同名包均为过程候选，不向新用户交付。
- 未生成独立 SHA 文件；内部清单用于正常完整性检查，不要求接收者手工校验。

## 实测结果

| 范围 | 证据与边界 | 结论 |
|---|---|---|
| Windows 运行环境 | GitHub 托管 Windows runner，官方 Python 3.12.10 x64 embedded；PowerShell 下载器无需系统 Python/pip/uv | PASS；不是 Windows 10/11 豆包 GUI |
| Windows 回归 | 95 项：92 通过、3 条件跳过（2 个私有历史索引夹具、1 个 ffmpeg 可选项） | PASS，无失败 |
| Windows 干净目录 | 无 .git，中文/空格路径；PATH 无 Git/Python/uv；外网阻断；包内 Python 和 8 个 wheel | PASS |
| Windows 完整启动 | 六个 healthcheck 均退出 0；Phase 3/4/5 PASS，Phase 1/2/6 在线连接器、可选 OCR/ASR、私有历史数据项 PARTIAL | 必需本地路径通过 |
| Windows 资料与迁移 | 两份生成 PDF：登记、页级检索、重复运行、移动至另一中文/空格目录、重启后来源文件存在 | PASS；私有课程未上传 CI |
| Mac 回归 | 最终 main 的 unittest 95 项全部通过 | PASS |
| 七天加速模拟 | 最终 main 后端 19 项检查、7 个逻辑日 checkpoint；三科、复习、离线补写、重启、周报、备份 | PASS；0 外部调用、0 正式写入 |
| 全部资料 | 两目录 349 文件：121 MP4、209 PDF、16 DOCX、1 RAR、1 PNG、1 空标记文件 | 清单与大小齐全 |
| PDF 可读性 | 209 份、8,128 页均可打开，每份首屏渲染成功 | PASS；不是逐页内容审读 |
| 视频探针 | 121 视频均有视频轨与正时长 | PASS；未逐帧观看全部课程 |
| 豆包本地安装 | Mac 真实解压的完整资料包，自带环境启动；源文件随修复更新 | 必需路径无 FAIL；不是最终 ZIP 的 Windows GUI 测试 |
| 豆包资料索引 | 349 文件登记，2 PDF 共 44 页首批索引；真实文件/页码命中 | PASS；未全量 OCR/ASR |
| 新飞书状态库 | 独立测试 Base、15 表；空画像 1、topics 10、resources 2、audit 13 | PASS；未继承旧用户进度 |
| 初始化重放 | 新增 0、更新 0；topics 10/10 主键唯一 | PASS（真实回读） |
| 真实项目创建 | 豆包在同账号官方网页创建测试项目，桌面侧栏同步可见 | PASS；既有项目保留 |
| 测试训练写入 | 明确标记模拟：会话 1、events 6、evidence 9、mastery 5、pending review 3、audit 20；checkpoint 七字段回读 | PASS；只写测试 Base |
| 新会话恢复 | 辅助选择桌面本地电脑及测试项目；仅给 project 路径及恢复指令；豆包读取配置并回读 checkpoint、5 掌握度、3 复习项，实际打开 PDF 第 1 页 | PASS（客户端点击辅助）；恢复 0 状态写入 |

## 发现与修复

1. 离线误入 Git/网盘流程：独立离线协议使用包内资料，无需这两项服务。
2. 新用户继承旧背景：改为空档案，旧成绩、观看进度和职业背景不作为接收者事实。
3. 私有片段依赖固定目录/数量：适配实际 catalog、片段和多个视频来源。
4. 新机缺少 Python：附 Mac 便携环境、Windows 官方嵌入式环境与 wheel；Git 安装增加 PowerShell 下载器。
5. Windows 编码/路径：显式 UTF-8、去掉 Mac 专有临时路径；嵌入式 _pth 根路径改为 `../../`，避免落到 .runtime；测试目录显式包化。
6. Windows 验收自身：修复 os.environ 转 dict 后大小写语义，以及 8.3 临时别名和长路径误判。此前失败日志仍保留，未改写为成功。
7. 飞书重复写入：豆包误解析 CLI 回读后产生 10 个重复 topics，识别后移除其误写批次；再次验证唯一主键及零增量。新增协议：识别 data.fields/data.data，未知不是空表，稳定 request/audit ID，只补缺失行。这是协议修复/真实回归，不是新增服务端唯一约束。
8. Base 写死：从当前 project-state.json 读取真实绑定，不从测试库漂移到正式库。
9. 云电脑误判：真实云任务可读飞书却无法读本机包，记录 PARTIAL。增加桌面本地入口、带 project 路径的短恢复提示词；真正本地新会话已通过。
10. 未发现项目级持久文件/指令入口：不把首条聊天说明冒充持久绑定。使用本机配置和带路径恢复提示词。
11. 健康检查误报：不把其他项目提醒算成本测试冲突；完整离线包不因网盘未登录降级。已修改技能及契约断言。
12. 芝士架构 anti-hack：停止自动读取，不绕过；官方界面、提交后截图/人工简表兜底，本地 PDF 训练继续。

## 接收者须知及未覆盖范围

- 先在豆包桌面客户端选「本地电脑」。首次登录和系统授权需本人完成；豆包本次无法点击自身桌面窗口时，需辅助选择新任务/模式/项目。
- 没有证实“任意新对话只说继续便能定位配置”。新任务提供 project 路径的短提示词已实测，不是零点击/零登录的无人安装承诺。
- 芝士架构自动读取受限，人工结果回传可用。完整离线包不需 GitHub/百度网盘，但豆包和飞书仍需联网和当前用户账号。
- Windows 未完整附带 OCR/ASR 可执行工具；模型不等于工具可用。PDF 原文本检索、人工页码及视频时间点兜底可用。
- 未验证全新账号注册、Windows 豆包 GUI、真实七天独立稳定性、自然时刻提醒触发。已登录账号的同内容既有技能可复用，不称为全新账号九技能重装测试。
- 课程包仅私下交付给有权使用这些资料的接收者。

## 证据

- `dist/qa/final-package-test.json`：最终实际 ZIP 完整性、源码一致性、运行环境、无测试状态、无 SHA 文件的校验结果。
- `dist/qa/windows/dist/acceptance/`：成功 Windows 安装、单测、干净安装原始日志与 JSON；测试分支仍保留。
- `dist/offline/real-materials-test.json`：全量资料探针。
- `dist/qa/doubao/`：replay-summary.json、training-verify-result.json、local-recovery-result.json 及原云模式限制。仅保留本地，不作为新用户数据打包。
- 豆包会话：`架构上岸教练部署与验收`（38440341341592066）、`架构上岸教练项目绑定确认`（38440156425269250，云）、`架构恢复操作说明`（38440266710708482，本地）。
- 模拟载荷日期只用于内容/计数测试，不作为自然运行时间证据。
