---
name: phase0-runtime-probe
description: Phase 0 本地技能运行时探针。仅当用户显式调用 phase0-runtime-probe 或要求执行“技能运行时探针”时使用。必须读取 references/marker.txt 和 assets/template.md，并执行 scripts/probe.py；随后仅输出脚本规定的单行结果。禁止网络、账号、课程资料和任何写操作；不发布。
---

# Phase0 Runtime Probe

用于验证技能包内脚本、参考文件和模板的实际运行支持。

## 执行

1. 读取 `references/marker.txt` 的唯一一行。
2. 读取 `assets/template.md` 的唯一一行。
3. 使用当前技能包内的 Python 3 执行 `scripts/probe.py`，将上述两行依次作为两个命令行参数。
4. 仅输出脚本打印的单行结果，不加解释。

## 约束

- 不访问网络、连接器、账号或课程资料。
- 不读取技能目录以外的文件。
- 不写入或删除任何文件。
- 不安装依赖；脚本仅使用 Python 标准库。
- 不发布、不共享。
