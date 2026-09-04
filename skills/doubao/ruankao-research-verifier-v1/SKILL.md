---
name: ruankao-research-verifier-v1
description: 软考官方信息、标准与当前技术资料核验技能。涉及考试日期、报名、规则、教材口径、标准或可能变化的工程事实时使用。优先官方原始来源，记录核验日期，区分 exam_view 与 industry_view；不确定项标待核验。
---

# Ruankao Research Verifier v1

## 来源优先级

`官方考试大纲与通知 > 官方教程/教材 > 经核验真题解析 > 用户授权课程 > 国家/行业标准与官方技术文档 > 高质量网络资料 > 普通文章 > 模型记忆`。

考试日期、报名、准考证和规则必须查询全国或用户所在地区的官方站点，记录 `verified_at/source_title/source_url/region`。某地区通知不能外推到所有地区。

## 口径

对可能冲突的结论分别输出：

- `exam_view`：教材/大纲/真题所需作答口径及来源；
- `industry_view`：当前工程实践及官方技术来源；
- `conflict_note`：差异和考试作答建议。

无法从原始来源确认时标记 `PENDING_VERIFICATION`，绝不让网络新观点静默覆盖考试口径。

## 输出与错误

返回 `status/data/error/audit_id`，data 含查询日期、原始链接、适用地区/版本和置信状态。错误包括 `OFFICIAL_SOURCE_NOT_FOUND`、`REGION_REQUIRED`、`SOURCE_CONFLICT`、`PENDING_VERIFICATION`。

## 安全边界

不绕过付费墙、登录、CAPTCHA 或 robots 限制；不转载大段受版权保护内容；不把模型记忆伪装成检索结果。
