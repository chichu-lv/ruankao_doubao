#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "03_豆包工作伙伴_最终系统指令模板.md"
TARGET = ROOT / "deployment" / "doubao" / "system-instructions-v1.md"
REPLACEMENTS = {
    "{{...}}": "所有部署占位符",
    "{{healthcheck_skill}}": "ruankao-healthcheck-v1",
    "{{state_connector}}": "飞书连接器中的私人 Base ArchitectPass State v1",
    "{{materials_skill}}": "ruankao-materials-v1",
    "{{cheko_skill}}": "cheko-practice-v1",
    "{{assessment_skill}}": "ruankao-assessment-v1",
    "{{case_skill}}": "ruankao-case-coach-v1",
    "{{essay_skill}}": "ruankao-essay-coach-v1",
    "{{review_skill}}": "ruankao-review-scheduler-v1",
    "{{research_skill}}": "ruankao-research-verifier-v1",
    "{{project_fact_store}}": "ArchitectPass State v1 所引用的私人脱敏项目事实库（未初始化时必须报告缺口）",
    "{{minutes}}": "<可用分钟数>",
    "{{energy}}": "<低/一般/高>",
}


def main() -> int:
    rendered = SOURCE.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        rendered = rendered.replace(old, new)
    rendered = rendered.replace(
        "# 豆包工作伙伴“架构上岸教练”——最终系统指令模板",
        "# 架构上岸教练 — 豆包私有项目系统指令 v1",
    )
    rendered = rendered.replace(
        "在开始任何训练前，调用 `ruankao-healthcheck-v1` 核对以下能力：",
        "以 `ruankao-controller-v1` 编排完整会话。在开始任何训练前，调用 `ruankao-healthcheck-v1` 核对以下能力：",
    )
    rendered = rendered.replace(
        "系统代码、技能、连接器、状态库和资料管线已经由 Codex 部署。",
        "系统代码、技能、连接器、状态库和资料管线已经按本仓库自举协议部署。",
    )
    rendered = "\n".join(
        line for line in rendered.splitlines()
        if not line.startswith("> 本模板由 Codex 在部署时写入豆包工作伙伴。")
    ) + "\n"
    if "{{" in rendered or "}}" in rendered:
        raise SystemExit("unresolved deployment placeholder")
    header = (
        "<!-- ArchitectPass private project instruction v1; generated from the retained product baseline. -->\n\n"
    )
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(header + rendered, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
