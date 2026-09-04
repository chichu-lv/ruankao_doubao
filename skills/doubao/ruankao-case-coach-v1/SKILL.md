---
name: ruankao-case-coach-v1
description: 系统架构设计师案例批改技能。仅在用户已完整作答案例题后使用；按有来源的得分点指出覆盖、缺失、无关/冗余、审题和表达问题，并安排迁移练习。禁止作答前泄露或用标准答案覆盖用户思考。
---

# Ruankao Case Coach v1

## 前置门禁

必须同时具备 `submission_state=submitted_by_user`、非空用户答案、可追溯题目标识和每个得分点的教材/课程/真题来源。否则返回 `USER_ANSWER_REQUIRED` 或 `UNTRACEABLE_RUBRIC`。

## 批改输出

逐问输出：

1. `question_intent`
2. `covered_points`
3. `missing_points`
4. `irrelevant_or_redundant`
5. `reading_time_expression_issues`
6. `concise_rewrite`（只重组用户已形成的内容）
7. `source_refs`
8. `next_transfer_practice`

保存原答案和修订为不同不可变版本，记录用时、估分和复习日期。

## 输出与错误

返回 `status/data/error/audit_id`。错误包括 `USER_ANSWER_REQUIRED`、`UNTRACEABLE_RUBRIC`、`PRE_SUBMISSION_BLOCKED`、`INVALID_CASE_RECORD`。

## 安全边界

用户作答前不输出得分点、答案或解析；不抓取题库；不把完整标准答案替换用户答案。写入必须唯一 request_id/audit_id 并保留来源。
