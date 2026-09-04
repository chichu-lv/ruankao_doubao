# Backup and restore

Production export is requested from the private Feishu state workflow and must be explicitly confirmed because it may contain sensitive personal study data. The export must include every table, schema version and a canonical SHA-256 digest. `build_backup`, `export_json`, `export_csv_tables`, and `export_markdown` implement the local format.

Before restore:

1. verify the checksum and supported schema version;
2. create a new backup of current authoritative data;
3. require explicit user confirmation;
4. import immutable facts with their original IDs and replay request IDs;
5. recompute projections rather than trusting backed-up `mastery_state`;
6. read back counts and sampled hashes before reporting success.

`restore_backup` verifies both the requested target and a fresh backup of the current state, rejects stale rollback backups, requires `user_confirmed=True`, restores only the exact allowlisted table set, appends a restore audit, and reconstructs idempotency for current records whose audit hash matches. Production Feishu restore remains an explicitly confirmed workflow; it is never unattended.
