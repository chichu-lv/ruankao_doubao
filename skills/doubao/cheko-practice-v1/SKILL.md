---
name: cheko-practice-v1
description: 芝士架构安全练习技能。用户要求创建选择题/真题/错题任务、打开芝士架构或在用户提交后导入结果时使用。必须规定题量、限时、完成标准和置信度；用户作答时等待。绝不自动选答、提交、提前读解析或抓取题库。
---

# Cheko Practice v1

## 创建任务

输入必须包含 `subject/mode/target/question_count/time_limit_minutes/completion_standard/capture_confidence/navigation_route`。验证允许的可见路由后进入 `AWAITING_HUMAN`；导航失败时给出精确人工路径。

## 用户边界

用户本人选答案并提交。在收到明确完成信号与可见已提交结果之前：

- 不读取、展示或推断答案、正确答案、解析和关键提示；
- 不选择答案、不点击提交、不关闭或重开练习；
- 不复制题干、选项、题库或原始 HTML。

## 结果导入

仅在提交后，按 `官方导出 → 可见结果页 → 截图 → 手工简表/口述` 降级。只接收结果/题目标识、主题、正误、置信度、用时、错误类型、提交时间和版本化 UI 契约。错题要求 K/C/M/A/Q/T/E；低置信度正确题标记 G 并安排复习。

## 输出与错误

统一返回 `status/data/error/audit_id`。错误包括 `PRE_SUBMISSION_BLOCKED`、`FORBIDDEN_CONTENT`、`NAVIGATION_MISMATCH`、`UI_CONTRACT_MISMATCH`、`MANUAL_FALLBACK_REQUIRED`。

## 安全边界

禁止私有 API、自动答题/提交、绕过会员/CAPTCHA/访问控制和大规模复制。所有结果写入带唯一 request_id/audit_id，失败如实报告。
