# DB-018 Feishu probe-object deletion verification

- Observed at: 2026-09-04 10:57 Asia/Shanghai
- Authority: the user explicitly confirmed deletion immediately before execution.
- Scope: only the two stable object IDs recorded by DB-018.

## Pre-delete identity check

- Calendar event ID `f537c09c-5531-4bf9-9513-7c470a747cc7_0` read back title `P0-CALENDAR-PROBE`: exact match.
- Task GUID `6559d935-3aa0-455a-8646-d0e9180238b6` read back title `P0-TASK-PROBE`: exact match.

## Delete and post-delete readback

- The first calendar delete attempt used an invalid `--notify` value and did not complete. Doubao corrected the invocation and used the connector's explicit `--yes` confirmation gate.
- Calendar delete returned `ok: true`, `action: deleted`, and `apply_to: single`. A subsequent ID read returned a metadata tombstone with `status: cancelled`; title, description, visibility, and attendee content were cleared. This is recorded as deleted with a retained cancelled tombstone.
- Task delete returned `ok: true` and `data: {}`. A subsequent ID read returned `ok: false`, code `1470404`, subtype `not_found`, and a message stating that the task cannot be found or has been deleted.
- Doubao reported that it did not modify or delete any other calendar event, task, or object, did not share anything, and did not use any platform other than Feishu.

