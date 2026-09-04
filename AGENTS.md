# Repository operating rules

This repository implements the private `ArchitectPass / 架构上岸教练` system.

## Authority and scope

- Treat `01_豆包软考私教系统_Codex开发说明书.md` and `04_验收清单.md` as non-optional product and acceptance baselines.
- Treat `02_交给Codex的总执行指令.md` as the execution mandate.
- Keep 豆包 as the final user-facing controller. Do not replace it with another model.
- Do not implement platform-specific skill or connector formats until Phase 0 evidence confirms the current 豆包 format.

## Safety and data handling

- Keep partners, skills, connectors, evidence, and user materials private by default.
- Never commit passwords, cookies, OTPs, API keys, access tokens, or unredacted company-confidential facts.
- Never bypass DRM, paywalls, membership limits, CAPTCHAs, or private APIs.
- Never automate answering or submitting 芝士架构 questions, and never expose answers before the user submits.
- Require explicit confirmation for deletion, publication, payment, permission changes, bulk overwrite, and sensitive-data export.
- Record failures truthfully; never claim that a UI action, write, import, or export succeeded without evidence.

## Engineering rules

- Preserve raw learning events and mastery evidence; derive mastery state reproducibly.
- Give every write operation an idempotency request ID and an audit ID.
- Restrict tools to allowlisted operations and paths; never expose arbitrary SQL, Shell, or filesystem access to 豆包.
- Keep source references traceable to PDF pages, video timestamps, visible question/result identifiers, or original web sources.
- Maintain fallbacks so automation failure does not block the user's study session.
- Update `docs/progress.md` and the relevant test record at the end of every phase.

## Phase gates

- Phase 0 must produce the capability matrix, screenshots/logs, an actual minimal skill sample, ADR-001, and a risk list.
- Do not enter large-scale implementation until every decision-gate capability in section 7.3 of the product specification has a feasible, evidence-backed path.
- Final completion requires all applicable checks in `04_验收清单.md`, including a seven-day independent pilot.
