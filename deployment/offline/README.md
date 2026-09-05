# 私有离线交付包

此方案用于 GitHub 或百度网盘暂时不可访问时，从一个本机压缩包部署。压缩包包含正式 `main` 项目快照、九个预构建技能包、两个授权目录中已下载的资料，以及本机已有的私有模型和派生转写。它不包含 Git 历史、账号、密码、Cookie、验证码或令牌。

已有索引不会原样打包，因为其中可能含旧电脑的绝对路径；豆包应在解压位置根据材料哈希重建索引。这样可以避免泄露本机用户名，也不会在换目录后指向失效文件。

## 构建前提

先通过百度网盘官方界面把需要离线保留的资料放到同一个父目录，父目录下必须保留两个精确目录名：

- `00、【推荐】【26年10月】wen老师架构课程（第二版）`
- `5、【2026年05月】芝士架构系统架构设计师`

默认构建会核对 `materials/manifests/authorized-sources-v1.json` 当前声明的每个文件；缺少任一声明文件就拒绝生成“完整”包。远端目录继续新增文件后，应先更新清单再重建。

## 构建

先运行：

```text
python3 scripts/bootstrap_local.py --prepare-only
```

再使用 `.venv` 中的 Python：

```text
.venv/bin/python3 scripts/build_offline_bundle.py --materials-root "/绝对路径/资料父目录"
```

输出位于忽略提交的 `dist/offline/`。如果只为验证流程而允许资料缺失，显式增加 `--allow-incomplete`；文件名和内部 manifest 都会标为 `PARTIAL`，不得作为完整备份。

生成后立即校验压缩包内的资料哈希、路径和九个预构建技能：

```text
python3 scripts/verify_offline_bundle.py "dist/offline/architectpass-offline-1.1.1.zip"
```

## 使用

不要把大压缩包上传到豆包聊天。让豆包使用本地电脑解压后读取包内 `ArchitectPass-offline/README-OFFLINE.md`，这样不受聊天附件大小限制。豆包、飞书和芝士架构使用接收者自己注册并登录的账号；离线包不会复制这些账号或权限。

实际安装协议是 `deployment/offline/bootstrap-v1.md`。新用户档案不带原用户观看进度或练习记录。资料清单和首批页级索引由 `scripts/prepare_offline_materials.py` 在解压位置生成，重复运行会复用已索引内容。

完整包附带 Windows 10/11 x64 与 Apple 芯片 Mac 的 Python 3.12 和依赖。Windows 在 project 中运行 `scripts\start_windows.cmd`，Mac 运行 `bash scripts/start_macos.sh`，均无需网络安装本地组件。Windows 使用官方 Python 3.12.10 嵌入式运行环境，依赖直接随应用部署，不修改系统 Python。建议解压至 `C:\AP` 等短路径。具体平台的实测结果以随交付的测试结论为准。模型文件不等于 OCR/ASR 可执行程序，缺少这些程序时使用本地文件阅读和精确页码/时间点。

运行环境来源：[Python 官方 Windows 发行](https://www.python.org/downloads/release/python-31210/)。

本包含有受授权范围约束的课程材料，只能私下保存和用于个人学习，不得发布、分享或提交到 Git。建议存放在加密磁盘或系统受保护目录；生成器不会假装普通 ZIP 自带可靠加密。
