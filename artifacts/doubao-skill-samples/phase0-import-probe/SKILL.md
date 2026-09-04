---
name: phase0-import-probe
description: 本地导入审计探针。仅用于验证当前豆包版本能否从本地 .skill 包导入技能。当用户显式调用 phase0-import-probe 或要求执行“本地导入探针”时使用。接收可选文本 input，返回严格格式 IMPORT_OK:<input>；未提供 input 时返回 IMPORT_OK。禁止访问网络、本地文件、连接器或任何账号数据；不包含脚本或第三方依赖；不发布。
---

# Phase0 Import Probe

只验证本地技能包的导入与调用链。

## 行为

1. 提取调用方提供的可选文本参数 `input`。
2. 若提供 `input`，仅输出一行：`IMPORT_OK:<input>`。
3. 若未提供 `input`，仅输出一行：`IMPORT_OK`。

## 约束

- 不访问网络、本地文件、连接器或任何账号数据。
- 不包含脚本，不依赖第三方工具或库。
- 不发布、不对外分发。
- 除固定输出外不产生其他副作用。
