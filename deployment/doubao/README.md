# Doubao private deployment v1

This directory is the production install source. Its skill package contract is a ZIP containing one same-name top-level skill directory, with `SKILL.md` inside that directory. The current Doubao UI must still be checked before installation.

Read `execution-context-v1.md` first. The current Doubao is the installer, not an external Codex developer. Confirm a real local-computer target before installation. Never open a second Doubao session or log into Doubao in a virtual desktop as a fallback. If self-UI control is unavailable, request the exact user click and verify it; preserve completed deployment steps on recovery. This is not a verified zero-assistance installation promise.

The delivery path is a public repository link plus the root-README prompt. Prefer an anonymous main source ZIP, not Git installation. On Windows, `scripts/install_public_windows.ps1 -FetchOnly` retrieves the source without Git, Python, SSH or a GitHub account; read the baselines, then resume the same entry without FetchOnly to provision the local runtime. Doubao must follow `bootstrap-v1.md`. No prior project, skill or development artifact is a prerequisite.

The two Baidu Netdisk course folders are runtime-private sources, not Git payloads. Prefer the installed, logged-in Windows official client and verify only the roots in `project-v1.json`, then download and index files needed for the current unit. Client login does not imply browser login or existing local downloads. A shared material account does not authorize inheriting the owner's learning state. If client automation is unavailable, guide the user through the exact download and resume from the local file. Raw courses, text, transcripts and indexes remain local. Missing OCR/ASR tooling is a truthful `PARTIAL` with manual page/timestamp fallback.

## Build and static verification

Run `python3 scripts/bootstrap_local.py`. The Python-3.9-compatible launcher discovers or provisions a private Python 3.11+ environment, installs the project, runs the local health checks and writes reproducible packages plus SHA-256 values to ignored `dist/doubao-skills/`. Source `SKILL.md` files remain version controlled under `skills/doubao/`.

If GitHub or Baidu Netdisk may be unavailable later, build the private local archive described in `deployment/offline/README.md` while both authorized course folders are still accessible. The archive is never a Git payload and never carries account credentials.

## Safe install

1. Open Doubao `技能 · 连接器 · 伙伴` → personal skills → import local skill.
2. Select one versioned ZIP. The archive member must be `<skill-name>/SKILL.md`; keep visibility private and do not publish.
3. Verify the imported name ends in `-v1`, remains enabled and does not replace any earlier skill.
4. Invoke an inert validation prompt that asks only for the skill name, version and safety boundary. Do not use real course, Cheko or company data in install validation.
5. Repeat for all nine packages and record visible evidence.
6. Bind the skills to the isolated private project `架构上岸教练`. Do not modify or reuse the older `系统架构设计师 AI Tutor` project or its `pass_ai` workspace.
7. Install the rendered system instructions. If the project surface has no persistent instruction field, attach the file as private project context and record the limitation truthfully.

Resolve the project root from the actual source ZIP directory (or existing main checkout). Source ZIPs have no .git and must not be subjected to Git working-tree checks. Verify the exact child folder before binding; never select a parent. If project-level file binding is unavailable, use the local configuration and directory-based recovery prompt, not a claim that chat history is persistent project configuration.

## Scheduling

Daily and weekly prompt templates are read-only. Saturday 20:00 Asia/Shanghai is a suggested weekly time; configure reminders using the current user's preference. Existing installed schedules are retained. Scheduled writes remain disabled.

## Update and rollback

- Never upload a same-name replacement: replacement may be irreversible and may not retain version history.
- Build a new versioned name (`-v2`, etc.), install it disabled, validate it, then enable it and disable the prior version.
- Roll back by disabling the new version and re-enabling the earlier version. The exact source and deterministic ZIP hash remain in the corresponding Git commit/build manifest.
- Do not delete a skill unless the user explicitly confirms deletion after the exact target is re-read.

## Platform fallback

If the current account has no private custom-partner entry, use a new isolated private Doubao Project named `架构上岸教练`. If it has no persistent project-instruction field, attach `system-instructions-v1.md` as private project context and explicitly adopt it in the initialization message. Report either limitation truthfully.
