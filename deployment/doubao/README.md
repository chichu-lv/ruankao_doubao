# Doubao private deployment v1

This directory is the install source for Phase 5. It follows the real Doubao 2.27.11 package shape proven in Phase 0 and Phase 5: a ZIP containing one same-name top-level skill directory, with `SKILL.md` inside that directory.

The final delivery path is Git-driven: the user gives Doubao the private repository link plus the short root-README prompt. Doubao must follow `bootstrap-v1.md` from a clean project context. The current machine's installed skills are validation evidence, not a prerequisite or hidden dependency.

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

The observed macOS native folder picker did not reliably preserve the exact child-folder selection through computer automation. No parent directory was saved. Until exact project-folder binding is manually verified, use only the allowlisted absolute repository path in a local-computer task and keep this limitation visible in health reports.

## Scheduling

Daily and weekly prompt templates are read-only. Their execution times remain unset until the user confirms preferred times. Do not enable scheduled writes. Creating, changing or deleting an external task remains a confirm-at-action operation.

## Update and rollback

- Never upload a same-name replacement: the observed client warned that replacement is irreversible and offered no version history.
- Build a new versioned name (`-v2`, etc.), install it disabled, validate it, then enable it and disable the prior version.
- Roll back by disabling the new version and re-enabling the earlier version. The exact source and deterministic ZIP hash remain in the corresponding Git commit/build manifest.
- Do not delete a skill unless the user explicitly confirms deletion after the exact target is re-read.

## Known platform limit

Phase 0 found no private custom-partner creation entry on this account. A new isolated private Doubao Project named `架构上岸教练` is therefore the evidence-backed persistent container; do not claim that a separate custom partner or persistent project-level instruction field exists.
