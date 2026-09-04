import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LightweightMaterialImportTests(unittest.TestCase):
    def test_progress_import_does_not_require_pdfplumber(self) -> None:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT / "backend")
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "sys.modules['pdfplumber'] = None; "
                    "from architectpass_materials.progress import next_review_action; "
                    "assert callable(next_review_action)"
                ),
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
