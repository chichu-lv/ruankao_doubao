# Doubao private deployment v1

This directory is the production install source. Its skill package contract is a ZIP containing one same-name top-level skill directory, with `SKILL.md` inside that directory. The current Doubao UI must still be checked before installation.

The delivery path is Git-driven: the user gives Doubao the private repository link plus the root-README prompt. Doubao must follow `bootstrap-v1.md` from a clean project context. No prior local project, installed skill or development artifact is a prerequisite.

The two Baidu Netdisk course folders are runtime-private sources, not Git payloads. During bootstrap, Doubao must use the user's authenticated official Baidu interface to verify only the exact roots listed in `project-v1.json`, then incrementally index files needed for the current study unit. Raw courses, extracted text, transcripts and indexes remain local and ignored by Git. Missing local OCR/transcription tooling is a truthful `PARTIAL` with an official-UI/manual page-or-timestamp fallback, not an installation failure.

## Build and static verification

Run `python3 scripts/phase5_healthcheck.py`. Reproducible packages and SHA-256 values are written to ignored `dist/doubao-skills/`. Source `SKILL.md` files remain version controlled under `skills/doubao/`.

## Safe install

1. Open Doubao `技能 · 连接器 · 伙伴` → personal skills → import local skill.
2. Select one versioned ZIP. The archive member must be `<skill-name>/SKILL.md`; keep visibility private and do not publish.
3. Verify the imported name ends in `-v1`, remains enabled and does not replace any earlier skill.
4. Invoke an inert validation prompt that asks only for the skill name, version and safety boundary. Do not use real course, Cheko or company data in install validation.
5. Repeat for all nine packages and record visible evidence.
6. Bind the skills to the isolated private project `架构上岸教练`. Do not modify or reuse the older `系统架构设计师 AI Tutor` project or its `pass_ai` workspace.
7. Install the rendered system instructions. If the project surface has no persistent instruction field, attach the file as private project context and record the limitation truthfully.

Resolve the repository root from the current `main` checkout. Bind it only after the exact child folder is visibly verified. If the picker exposes a parent folder or cannot prove the selection, cancel the binding and use the exact resolved checkout path only in the current local-computer task.

## Scheduling

Daily and weekly prompt templates are read-only. The weekly target is the user-confirmed Saturday 20:00 Asia/Shanghai; the daily reminder stays unconfigured until the user separately confirms a time. Do not enable scheduled writes. Creating, changing or deleting any other external task remains a confirm-at-action operation.

## Update and rollback

- Never upload a same-name replacement: replacement may be irreversible and may not retain version history.
- Build a new versioned name (`-v2`, etc.), install it disabled, validate it, then enable it and disable the prior version.
- Roll back by disabling the new version and re-enabling the earlier version. The exact source and deterministic ZIP hash remain in the corresponding Git commit/build manifest.
- Do not delete a skill unless the user explicitly confirms deletion after the exact target is re-read.

## Platform fallback

If the current account has no private custom-partner entry, use a new isolated private Doubao Project named `架构上岸教练`. If it has no persistent project-instruction field, attach `system-instructions-v1.md` as private project context and explicitly adopt it in the initialization message. Report either limitation truthfully.
