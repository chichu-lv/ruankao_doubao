# ADR-009: Official folder skills as the local persistent bootstrap path

Date: 2026-09-06. Status: implementation candidate, complete clean deployment not yet passed.

## Evidence

The clean-user 1.1.4 attempt independently fetched source, built, located materials and created an empty 15-table state Base, but required nine manual uploads and instructed the user to bind system instructions through controls absent from the real Mac project dialog. Actual project controls expose only a name and local folder. A personal review-scheduler skill remained in the documented skill directory despite earlier UI-based cleanup evidence, so the attempt cannot establish clean-state success.

The current bundled `skill-creator-for-work/SKILL.md` was fully read. It requires ordinary skill folders in the active environment's existing `workspace/.user_skills`, with the parent resolved from actual provided skill paths; it explicitly finalizes folders rather than ZIPs. This is the supported extension surface, not client registry manipulation. Account-cloud installation and native sidebar projects remain separate, unproven capabilities.

Doubao itself used this official workflow to create an inert `architectpass-folder-probe-v1`. After confirming the empty work-page URL, a distinct new local task was given only “执行 ArchitectPass 文件夹探针。” and returned the private fixed marker. The expected marker and directory were not included in that new task's prompt. A prior keyboard shortcut failed to create a new task; its same-conversation response is explicitly excluded from cross-task evidence.

During developer probe validation Doubao reported adding PyYAML to the user environment; this is a test-environment difference and not proof of a dependency-free fresh machine. The new installer uses only the Python standard library. No credentials, native databases or private APIs were used by Codex.

## Decision

Prefer the current official folder path after verifying it exists and belongs to the active local environment. Install only the nine declared folders with a per-skill installation binding to the real source root. Skills load the system instructions and live state binding from that root even when a new task has a different working directory.

Keep manual ZIP upload as a fallback. Native sidebar projects are optional navigation containers when their controls are unavailable; a local workspace is an equivalent persistent entry only after actual fresh-task recovery passes. Never report a native project/account skill created based solely on filesystem presence.

The installer preflights every target, reuses identical content/binding, refuses different existing content before writes, records request/audit IDs, and reports `FILES_READY_DISCOVERY_UNVERIFIED`. It does not inspect or modify the client registry. Cleanup must verify both UI and the documented skill-folder source, then new-task discovery. Retain all other projects/skills.

## Verification still required

Main 1.1.5 / 1707c25 has 108 local tests passing, including binding, repeat, conflict, unrelated-skill preservation and archive inclusion. This is not the final acceptance. A complete new clean deployment, nine-skill discovery, source retrieval, live health check, first training and fresh-task state recovery remain required. Gitee and old offline ZIPs do not update automatically.
