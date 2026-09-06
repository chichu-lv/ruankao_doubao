---
name: ruankao-assessment-v1
description: 软考闭卷测评与掌握证据技能。用于视频/阅读后的闭卷复述、分层测试、错误分类、变式练习和 0—5 掌握度更新。必须先让用户输出，不能把看过、听懂或一次猜对当作掌握。
---

# Ruankao Assessment v1

## 证据阶梯

空档案、空表、没有历史记录不是“未学过”证据。没有真实测评时 `assessment=NOT_ASSESSED`，掌握度保持未知，不填 0 级、不分类 K，不诊断知识缺失；不能把系统刚建档说成用户第一次接触课程。

验收测试、虚构样例和明确的模拟复述仅用于流程验证，不属于真实考试模拟练习。保存时标记 `evidence_scope=acceptance_test`、`mastery_eligible=false`、`assessment=NOT_ASSESSED`，允许只保存位置；不得生成真实 mastery_evidence、薄弱点、复习排期，也不得在下一会话把测试措辞当成用户能力。真实限时模拟考试不因“模拟”二字自动排除，依据用户声明的用途区分。

`viewed < open_book_recall < closed_book_recall < choice_untimed < choice_timed < case_points < essay_application < timed_mock`。

掌握度上限：看/读=1，闭卷复述=2，稳定选择题=3，案例得分点=4，论文真实项目展开=5。一次选择题正确不能建立 3 级；低置信度正确必须分类 G。

## 流程

1. 在不暴露答案的前提下给出闭卷问题或变式任务。
2. 等待用户完整输出；未输出返回 `AWAITING_HUMAN`。
3. 依据来源和 rubric 评分 `score/confidence/difficulty/timed`。
4. 分类 K/C/M/A/Q/T/E/G，保留用户原证据。
5. 生成新的 immutable mastery_evidence，并触发可复现 mastery_state 重算。

## 输出与错误

返回 `status/data/error/audit_id`，data 包含 `evidence_type/score/confidence/error_type/source_id/mastery_ceiling`。错误包括 `USER_OUTPUT_REQUIRED`、`UNTRACEABLE_SOURCE`、`INVALID_EVIDENCE`、`INSUFFICIENT_REPETITION`。

## 安全边界

禁止在测试前给答案，禁止仅凭解释流畅度提升掌握度，禁止覆盖原始证据。写入使用唯一 request_id/audit_id。
