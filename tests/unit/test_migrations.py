import tempfile
import unittest
from pathlib import Path

from architectpass_state.errors import StateError
from architectpass_state.migrations import migration_plan


class MigrationTests(unittest.TestCase):
    def test_repository_migration_chain_reaches_v1(self) -> None:
        directory = Path(__file__).resolve().parents[2] / "schemas" / "migrations"
        plan = migration_plan(directory, 0, 1)
        self.assertEqual(["0001-initial"], [item["migration_id"] for item in plan])

    def test_migration_gap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(StateError) as error:
                migration_plan(Path(directory), 0, 1)
        self.assertEqual("MIGRATION_GAP", error.exception.code)


if __name__ == "__main__":
    unittest.main()
