# 新用户干净沙盒复验 — 1.1.0

日期：2026-09-04

被测发布：

- `main`：`0a74fdb64dc765b1572630317a317f461bbb1cb7`
- 版本：`1.1.0`
- 目标：关闭 1.0.1 新用户验收中的 Python 自举、ZIP 可复现性和 Phase 2 状态语义问题，并验证私有离线压缩包方案。

## 修复结果

| 原问题 | 1.1.0 结果 | 证据 |
|---|---|---|
| 系统 Python 3.9 无法直接构建 | `PASS` | 在全新远端克隆中只运行 `python3 scripts/bootstrap_local.py --prepare-only`；入口从 Python 3.9.6 启动，通过项目私有 `.runtime/` 自动下载 Python 3.12.13，在 `.venv/` 安装 9 个依赖。 |
| 两个独立克隆 ZIP 哈希不同 | `PASS` | 两个独立远端克隆生成的九个技能 ZIP，9/9 SHA-256 完全相同；ZIP 时间戳、权限、顺序和压缩级别固定。 |
| 缺本地 OCR/ASR 模型被报 FAIL | `PASS` | 不含任何私有模型的全新克隆运行 Phase 2，退出码为 0，输出 `SUMMARY: PARTIAL` 和官方界面人工页码/时间点兜底；契约或哈希错误仍为 FAIL。 |

全量测试：90/90 PASS。

全新克隆完整本地自举：`PARTIAL`，其中 Phase 3/4/5 PASS；Phase 1 仅因无实时飞书认证为 PARTIAL；Phase 2 仅因私有模型不在 Git 为 PARTIAL；Phase 6 仅因私有索引不在 Git 为 PARTIAL。该结果符合发布边界。

## 离线压缩包方案

正式实现：

- `deployment/offline/README.md`
- `deployment/offline/bundle-v1.json`
- `scripts/build_offline_bundle.py`
- `scripts/verify_offline_bundle.py`
- `backend/architectpass_offline/`

压缩包结构：

- `ArchitectPass-offline/project/`：正式 main 项目快照，不含 Git 历史；
- `ArchitectPass-offline/prebuilt-skills/`：九个可复现技能 ZIP；
- `ArchitectPass-offline/private-materials/`：两个精确授权目录中的实际本地文件；
- `ArchitectPass-offline/offline-manifest.json`：每个资料/运行时资产的大小与 SHA-256；
- `ArchitectPass-offline/README-OFFLINE.md`：无需 GitHub/Baidu 的豆包启动提示词。

安全行为：

- 默认必须存在清单声明的全部资料，否则拒绝生成“完整”包；
- `--allow-incomplete` 只生成文件名和 manifest 均标记 `PARTIAL` 的包；
- 拒绝符号链接、路径穿越和疑似凭据文件；
- 不包含 `.git`、账号、Cookie、Token、密钥；
- 不原样携带含旧电脑绝对路径的索引，解压后按哈希重建；
- 大文件在本地解压后交给豆包，不上传聊天附件或 Git。

## 真实样品

本机当前只有 24 个已登记资料文件中的 2 个，因此只生成并验证了 PARTIAL 样品：

- 文件：`dist/offline/architectpass-offline-1.1.0-PARTIAL.zip`（Git 忽略、本机私有）
- 大小：733,700,153 bytes（约 700 MB）
- SHA-256：`98b2a157a08850ac9433f13a7adb51fff31fd5410be91a28a3352c1a7240c4cf`
- 已含资料：2
- 缺少清单资料：22
- 运行时私有模型/转写资产：6
- 内置技能：9
- 校验器结果：`PARTIAL`，0 errors

从该 ZIP 在一个不访问 GitHub/Baidu 的全新目录解压并模拟安装：9/9 技能成功，2 个资料文件可见，`.git` 目录数为 0，含旧本机绝对路径的文件数为 0。

## 尚未满足的完整离线条件

必须先通过百度网盘官方界面下载当前清单缺少的 22 个文件，并确认两个远端目录的清单已经完整。只有默认构建（不加 `--allow-incomplete`）返回 `PASS`，才可把压缩包称为完整离线备份。

豆包、飞书和芝士架构账号不进入压缩包；接收者应自行注册并在官方界面登录。离线包只解决 GitHub 项目源与百度资料源不可访问的问题。
