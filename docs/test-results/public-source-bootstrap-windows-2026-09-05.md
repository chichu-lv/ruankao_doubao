# 公开链接 / 无 Git Windows 安装入口验收

日期：2026-09-05。版本：1.1.2。main：`6d29e7f`。结论：**公开源码下载与本地环境部署 PASS；Windows 豆包/网盘 GUI 未实测**。

## 用户范围

仓库已公开，用户允许开发记录也公开。新用户仅会使用豆包，不应安装 Git、配置 SSH/GitHub 或手输命令。目标 Windows 电脑会预先安装并登录百度网盘官方客户端，资料账号与提供者相同；这不代表共享学习档案或复制已有进度。本轮不修改账号权限、网盘文件或既有飞书状态。

## 变更

- 新增 `scripts/install_public_windows.ps1`：只依赖 Windows PowerShell，匿名下载 main 源码 ZIP，默认安装到当前用户 LOCALAPPDATA/ArchitectPass，无系统 Git/Python/uv 要求。
- FetchOnly 先下载项目；豆包读取产品/验收基线后再运行完整入口，自动获取项目内 Python 3.12.10 与八个依赖 wheel，执行六项健康检查、构建九个技能包。成功准备本地环境不等于豆包在线安装完成。
- `dist/bootstrap/public-source.json` 记录来源、引用、版本和时间。main 源码包不带 .git，不运行 Git 分支/工作树检查，不伪造未知的提交 ID。
- 重复执行恢复原快照，保留来源记录和用户文件；未知已有目录拒绝覆盖，由豆包选择新的项目目录。无自动升级、全局 PATH 修改或系统 Python 安装。
- README 提示词及自举/更新协议明确：用户只做本人登录/授权；豆包完成下载、环境、技能和状态部署。后续 Windows Python 命令使用项目私有解释器。
- 百度网盘优先使用已登录的 Windows 官方客户端，核对两个精确授权目录，按需下载、验证实际本机文件后索引。客户端登录不等于浏览器登录；客户端不可操作时引导具体文件下载，不假装自动化已完成。
- 同一资料账号不继承原用户观看进度、题目结果、掌握度或飞书状态。
- GitHub Actions 保持 `contents: read`，未重新启用任何测试分支写入权限。

## 实测

本地构建九技能 ZIP 成功，98 项 unittest 全部通过，git diff --check 无错误。

第一次 Windows 公共源码测试在提交 `0cbcb13` 通过：[运行 33944820371](https://github.com/chichu-lv/ruankao_doubao/actions/runs/33944820371)。补充默认 main 下载路径后，最终提交 `6d29e7f` 的完整 Windows 流程再次全部通过：[运行 33944955067](https://github.com/chichu-lv/ruankao_doubao/actions/runs/33944955067)。

最终工作流逐项 success：运行环境准备、离线启动、Windows 回归单测、无 Git/Python 的干净离线安装、无 Git/Python 的公开源码安装、测试结果 artifact 上传。

公开安装专项在真实 Windows runner 中：

1. 从公开 raw URL 匿名下载安装脚本，而非只执行 checkout 中的脚本。
2. PATH 仅保留 Windows 系统工具；断言 git/python/python3/uv 均不可用。
3. 下载公开固定提交源码 ZIP 到中文及空格路径，断言不存在 .git，来源记录与提交一致。
4. 从下载的源码执行运行环境准备和完整六项健康检查；每项退出码为 0，在线/可选处理能力允许按真实结果 PARTIAL。
5. 确认九个技能 ZIP 生成；再次启动保留用户哨兵文件和原来源记录。
6. 不提供 Revision 参数，再次测试默认 main 下载地址；记录 source_ref=main、未知 source_commit=null，并确认不需要 .git。

本轮不把最初固定提交测试冒充默认 main 测试；最终运行确实覆盖两个地址。公开下载使用正常网络，另一个保留的干净离线测试继续覆盖阻断网络场景。

## 边界与交付

- Windows 豆包的首次权限弹窗、飞书登录、百度网盘客户端控制尚未在目标用户电脑逐屏实测；本轮是 Windows 本地安装链路测试，不是这些 GUI 能力的新通过证据。
- 网盘不可控时，用户可能需要按豆包提示下载指定文件，之后由豆包继续。登录、验证码、系统授权不能由豆包代替本人批准。
- 公共源码 ZIP 不含课程原文件。此前 26.71 GB 完整离线包仍是 1.1.1，本轮没有重建或覆盖它；本轮 1.1.2 更新用于公开链接入口。
- 测试证据：Actions 运行页面与 artifact；本地 `dist/qa/public-source-windows-ci.json` 保存逐步骤结论。没有生成独立 SHA 文件。
