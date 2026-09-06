---
name: ruankao-materials-v1
description: 私有软考资料检索与进度技能。用户要求查 PDF 页、视频时间段、打开百度网盘课程、记录已看位置或增量处理资料时使用。仅限两个授权课程范围和 ArchitectPass 私有材料目录；必须返回页码或时间戳，禁止公开上传和绕过网盘限制。
---

# Ruankao Materials v1

## 本地优先

本次授权本地课程已可读时，直接从真实索引读取或增量处理学习文件，不检索/调用百度网盘连接器，不为证明远端登录重复建立工具会话。远端状态为 `DEFERRED_NOT_REQUIRED_FOR_LOCAL_STUDY`，不是 PASS；只在缺少当前具体学习文件时处理网盘下载。资料和状态层的独立步骤继续，不因远端待核验阻塞本地训练。

同一连接器工具最多检索两次；取得 schema 不等于执行读取。仍不能调用时报告 CONNECTOR_NOT_CALLABLE，停止循环，使用本次绑定的本地资料。已下载的两个授权课程可用项目脚本 `scripts/prepare_downloaded_materials.py` 建立/查询 `materials/index/downloaded-catalog.json`，不能扫描其它下载内容或继承旧学习状态。

## 授权范围

- 百度网盘 `00、【推荐】【26年10月】wen老师架构课程（第二版）`
- 百度网盘 `5、【2026年05月】芝士架构系统架构设计师`
- 本项目私有 `materials/` 目录中已登记清单

## 操作

- `list_materials(filters)`：返回资源 ID、文件名、类型、校验和和处理状态。
- `search_materials(query, filters)`：PDF 返回文件名+页码+短片段；视频返回文件名+原视频开始/结束时间+短片段+置信度。
- `open_material(target)`：只接受清单内 resource_id/page 或 start/end；自动定位失败时输出人工路径。
- `record_video_progress(...)`：保存播放事实为 `played_unchecked`，不得直接提升掌握度。
- `process_new_material(...)`：按哈希增量处理；失败进入隔离并给出人工方案。

当前用户已学过的视频先诊断再定点回看；未知进度保持未知。OCR 仅用于普通提取失败的必要页；转写保留原视频时间轴。离线包从解压目录读取资料，使用 project/scripts/prepare_offline_materials.py 建立清单和页级索引；不要求登录百度网盘。

公开源码安装没有课程原文件。Windows 优先核对已安装并登录的百度网盘官方客户端，不因浏览器未登录而要求重复登录。只在两个授权目录下载当前所需资料，确认文件已下载完成且可读，再增量索引。客户端无法操作时引导用户完成精确文件下载，获得本机路径后继续；不得把客户端登录等同于已建立资料索引。共用网盘账号不代表共用学习档案，不继承其他用户进度。

## 输出与错误

统一返回 `status/data/error/audit_id`。常见错误：`PATH_NOT_ALLOWED`、`RESOURCE_NOT_FOUND`、`PARSE_FAILED`、`OPEN_FALLBACK_REQUIRED`、`LOW_TRANSCRIPT_CONFIDENCE`。

## 安全边界

不上传原始课程、不公开分享、不绕过 DRM/会员/下载限制、不访问授权范围外路径。写进度必须带唯一 request_id/audit_id 并回读验证。
