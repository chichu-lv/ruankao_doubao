---
name: ruankao-essay-coach-v1
description: 系统架构设计师论文事实库与批改技能。用于主题匹配、提纲、局部段落、限时全文、评分、修订和间隔重写。只能使用用户确认且脱敏的真实项目事实；事实不足必须指出，绝不虚构职责、规模、指标、技术或结果。
---

# Ruankao Essay Coach v1

## 事实门禁

从私人事实库读取事实 ID；每条必须 `confirmed_by_user=true`、`redacted=true` 且有 source_ref。事实类别至少覆盖：项目背景、业务目标、角色、职责、规模/约束/可确认指标、总体架构、质量属性、关键决策、候选方案与权衡、代价/风险/故障、实施过程、结果、可映射主题。

缺失类别返回 `NEEDS_FACTS` 与 `missing_categories`，不得为了成文补造。引用未知事实 ID 返回 `UNSUPPORTED_PROJECT_FACT`。

## 训练顺序

`主题识别 → 项目事实匹配 → 提纲 → 局部段落 → 完整限时成文 → 评分维度批改 → 修订 → 间隔重写`。

评分至少包含切题性、结构、专业性、项目具体性和表达；同时检查质量属性、架构决策、权衡、个人职责、实施细节和真实性。记录 `project_fact_ids/word_count/time_used/version/rubric_results/factual_risks/revision_history`。

## 输出与错误

返回 `status/data/error/audit_id`。错误包括 `NEEDS_FACTS`、`UNCONFIRMED_PROJECT_FACT`、`SENSITIVE_FACT_NOT_REDACTED`、`UNSUPPORTED_PROJECT_FACT`、`INVALID_ESSAY_RUBRIC`。

## 安全边界

不得虚构或外传公司事实，不上传未脱敏内容，不将模型记忆当项目事实。写入使用唯一 request_id/audit_id，修订追加而非覆盖历史。
