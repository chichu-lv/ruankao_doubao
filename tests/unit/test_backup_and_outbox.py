import json
import tempfile
import unittest
from pathlib import Path

from architectpass_state import InMemoryStore, StateService, WriteContext
from architectpass_state.backup import build_backup, export_csv_tables, export_json, export_markdown, restore_backup, safe_backup_path, verify_backup
from architectpass_state.errors import StateError
from architectpass_state.outbox import OfflineOutbox, PersistentOfflineOutbox


class BackupAndOutboxTests(unittest.TestCase):
    def test_real_feishu_canary_backup_fixture_verifies(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "phase1-feishu-canary-backup.json"
        verify_backup(json.loads(fixture.read_text(encoding="utf-8")))

    def test_backup_exports_json_csv_and_markdown(self) -> None:
        backup = build_backup({"topics": [{"topic_id": "t1", "name": "数据库"}]})
        verify_backup(backup)
        self.assertEqual(1, json.loads(export_json(backup))["schema_version"])
        self.assertIn("topic_id", export_csv_tables(backup)["topics"])
        self.assertIn("数据库", export_markdown(backup))

    def test_modified_backup_is_rejected(self) -> None:
        backup = build_backup({"topics": []})
        backup["data"]["topics"].append({"topic_id": "tampered"})
        with self.assertRaises(StateError) as error:
            verify_backup(backup)
        self.assertEqual("BACKUP_CHECKSUM_MISMATCH", error.exception.code)

    def test_backup_path_cannot_escape_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(Path(directory).resolve() / "ok.json", safe_backup_path(Path(directory), "ok.json"))
            with self.assertRaises(StateError):
                safe_backup_path(Path(directory), "../escape.json")

    def test_outbox_replay_is_safe_and_only_acks_success(self) -> None:
        outbox = OfflineOutbox()
        outbox.enqueue("req-1", "record_study_event", {"event_id": "e1"})
        outbox.enqueue("req-1", "record_study_event", {"event_id": "changed"})
        calls = []

        def sender(item):
            calls.append(item)
            return {"status": "error" if len(calls) == 1 else "ok"}

        outbox.replay(sender)
        self.assertEqual(1, len(outbox.pending()))
        outbox.replay(sender)
        self.assertEqual([], outbox.pending())
        self.assertEqual("e1", calls[1]["payload"]["event_id"])

    def test_persistent_outbox_survives_restart_and_acks_only_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            context = WriteContext("offline-req-1", "offline-audit-1", "unit-test")
            queued = PersistentOfflineOutbox(root)
            queued.enqueue("record_study_event", {"event_id": "offline-e1"}, context)

            restarted = PersistentOfflineOutbox(root)
            self.assertEqual("offline-req-1", restarted.pending()[0]["request_id"])
            restarted.replay(lambda item: {"status": "error", "audit_id": item["audit_id"]})
            self.assertEqual(1, len(PersistentOfflineOutbox(root).pending()))

            restarted.replay(lambda item: {"status": "ok", "audit_id": item["audit_id"]})
            self.assertEqual([], PersistentOfflineOutbox(root).pending())

    def test_persistent_outbox_enforces_ids_idempotency_and_operation_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outbox = PersistentOfflineOutbox(Path(directory))
            context = WriteContext("offline-req-2", "offline-audit-2", "unit-test")
            first = outbox.enqueue("update_profile", {"user_id": "u1"}, context)
            second = outbox.enqueue("update_profile", {"user_id": "u1"}, context)
            self.assertFalse(first["deduplicated"])
            self.assertTrue(second["deduplicated"])
            with self.assertRaises(StateError) as conflict:
                outbox.enqueue("update_profile", {"user_id": "u2"}, context)
            self.assertEqual("IDEMPOTENCY_CONFLICT", conflict.exception.code)
            with self.assertRaises(StateError) as blocked:
                outbox.enqueue("arbitrary_shell", {}, WriteContext("r3", "a3", "unit-test"))
            self.assertEqual("OPERATION_NOT_ALLOWED", blocked.exception.code)

    def test_persistent_outbox_rejects_path_escape_and_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(StateError):
                PersistentOfflineOutbox(root, "../escape.json")
            outbox = PersistentOfflineOutbox(root)
            outbox.enqueue(
                "update_profile",
                {"user_id": "u1"},
                WriteContext("offline-req-4", "offline-audit-4", "unit-test"),
            )
            path = root / "architectpass-outbox.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["pending"][0]["payload"]["user_id"] = "tampered"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(StateError) as tampered:
                PersistentOfflineOutbox(root)
            self.assertEqual("OUTBOX_CHECKSUM_MISMATCH", tampered.exception.code)

    def test_restore_requires_current_backup_confirmation_and_preserves_idempotency(self) -> None:
        store = InMemoryStore()
        service = StateService(store)
        original_context = WriteContext("restore-req-1", "restore-audit-1", "unit-test")
        service.invoke("update_profile", user_id="u1", patch={"timezone": "UTC"}, context=original_context)
        target = build_backup(store.snapshot())
        service.invoke(
            "update_profile", user_id="u1", patch={"timezone": "Asia/Shanghai"},
            context=WriteContext("restore-req-2", "restore-audit-2", "unit-test"),
        )
        current = build_backup(store.snapshot())
        restore_backup(
            store, target_backup=target, current_backup=current,
            context=WriteContext("restore-req-3", "restore-audit-3", "unit-test", user_confirmed=True),
        )
        self.assertEqual("UTC", store.read("user_profile", "u1")["timezone"])
        replay = service.invoke("update_profile", user_id="u1", patch={"timezone": "UTC"}, context=original_context)
        self.assertTrue(replay["data"]["deduplicated"])
        self.assertEqual(current["sha256"], store.read("audit_log", "restore-audit-3")["rollback_ref"])

    def test_restore_rejects_stale_pre_restore_backup(self) -> None:
        store = InMemoryStore()
        empty = build_backup(store.snapshot())
        service = StateService(store)
        service.invoke(
            "update_profile", user_id="u1", patch={"timezone": "UTC"},
            context=WriteContext("stale-req-1", "stale-audit-1", "unit-test"),
        )
        with self.assertRaises(StateError) as error:
            restore_backup(
                store, target_backup=empty, current_backup=empty,
                context=WriteContext("stale-req-2", "stale-audit-2", "unit-test", user_confirmed=True),
            )
        self.assertEqual("STALE_PRE_RESTORE_BACKUP", error.exception.code)


if __name__ == "__main__":
    unittest.main()
