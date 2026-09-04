import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from architectpass_materials import MaterialCatalog, MaterialImporter, MaterialSearch, next_review_action
from architectpass_materials.errors import MaterialError
from architectpass_materials.models import MaterialContext
from architectpass_materials.pdf import _needs_ocr
from architectpass_materials.video import (
    extract_audio,
    extract_audio_clip,
    probe_video,
    transcribe_audio_whisper_cpp,
)


ROOT = Path(__file__).resolve().parents[2]
MARKER = "ARCHITECTPASS_MATERIAL_FIXTURE"


def write_minimal_pdf(path: Path) -> None:
    stream = f"BT /F1 12 Tf 72 720 Td ({MARKER}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    document = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, payload in enumerate(objects, start=1):
        offsets.append(len(document))
        document.extend(f"{number} 0 obj\n".encode("ascii"))
        document.extend(payload + b"\nendobj\n")
    xref_offset = len(document)
    document.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    document.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        document.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    document.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(document)


def context(number: int, request: str | None = None) -> MaterialContext:
    return MaterialContext(request or f"material-req-{number}", f"material-audit-{number}", "unit-test")


class MaterialPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_directory = tempfile.TemporaryDirectory()
        self.fixture_root = Path(self.fixture_directory.name)
        self.fixture_pdf = self.fixture_root / "material-fixture.pdf"
        write_minimal_pdf(self.fixture_pdf)

    def tearDown(self) -> None:
        self.fixture_directory.cleanup()

    def test_watched_progress_requires_diagnosis_then_only_targeted_rewatch(self) -> None:
        observation = {
            "status": "played_unchecked",
            "watched_until_seconds": 611,
            "duration_seconds": 3631,
        }
        diagnostic = next_review_action(observation)
        self.assertEqual("diagnostic", diagnostic["action"])
        self.assertFalse(diagnostic["restart_from_beginning"])
        self.assertFalse(diagnostic["mastery_changed"])

        rewatch = next_review_action(observation, weak_ranges=((600, 611),))
        self.assertEqual("targeted_rewatch", rewatch["action"])
        self.assertEqual([{"start_seconds": 600, "end_seconds": 611}], rewatch["ranges"])
        self.assertFalse(rewatch["restart_from_beginning"])
        self.assertFalse(rewatch["mastery_changed"])

    def test_chinese_extraction_quality_selects_only_unusable_pages_for_ocr(self) -> None:
        self.assertTrue(_needs_ocr("75 1 150 45 http://example.test"))
        self.assertTrue(_needs_ocr("封面"))
        self.assertFalse(_needs_ocr("系统架构设计师需要理解可用性战术与心跳检测。"))

    def test_pdf_page_extraction_search_and_source_anchor(self) -> None:
        catalog = MaterialCatalog()
        importer = MaterialImporter(catalog, (self.fixture_root,))
        result = importer.import_file(
            self.fixture_pdf,
            context=context(1), copyright_scope="project_test_fixture",
        )
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["data"]["segment_count"])
        matches = MaterialSearch(catalog).search(MARKER)
        self.assertEqual(1, matches[0]["page"])
        self.assertFalse(matches[0]["ocr"])
        self.assertIn("snippet", matches[0])
        self.assertNotIn("text", matches[0])
        self.assertIn("#page=1", matches[0]["citation_anchor"])
        self.assertIn("#page=1", matches[0]["open_target"])

    def test_hash_deduplicates_same_pdf_across_requests(self) -> None:
        catalog = MaterialCatalog()
        importer = MaterialImporter(catalog, (self.fixture_root,))
        path = self.fixture_pdf
        first = importer.import_file(path, context=context(2), copyright_scope="project_test_fixture")
        second = importer.import_file(path, context=context(3), copyright_scope="project_test_fixture")
        self.assertFalse(first["deduplicated"])
        self.assertTrue(second["deduplicated"])
        self.assertEqual(1, len(catalog.resources))

    def test_identical_request_replay_is_idempotent(self) -> None:
        catalog = MaterialCatalog()
        importer = MaterialImporter(catalog, (self.fixture_root,))
        path = self.fixture_pdf
        first = importer.import_file(path, context=context(4), copyright_scope="project_test_fixture")
        second = importer.import_file(path, context=context(4), copyright_scope="project_test_fixture")
        self.assertFalse(first["deduplicated"])
        self.assertTrue(second["deduplicated"])
        self.assertEqual(1, len(catalog.audits))

    def test_catalog_export_replay_is_idempotent_and_conflicts_fail_closed(self) -> None:
        catalog = MaterialCatalog()
        importer = MaterialImporter(catalog, (self.fixture_root,))
        importer.import_file(
            self.fixture_pdf,
            context=context(14),
            copyright_scope="project_test_fixture",
        )
        with tempfile.TemporaryDirectory() as directory:
            target_root = Path(directory)
            export_context = context(15)
            target = catalog.export(target_root, "catalog.json", export_context)
            self.assertEqual(target, catalog.export(target_root, "catalog.json", export_context))
            with self.assertRaises(MaterialError) as error:
                catalog.export(target_root, "catalog.json", context(16))
            self.assertEqual("CATALOG_EXPORT_CONFLICT", error.exception.code)

    def test_path_outside_authorized_root_is_blocked(self) -> None:
        importer = MaterialImporter(MaterialCatalog(), (ROOT / "materials",))
        with self.assertRaises(MaterialError) as error:
            importer.import_file(
                self.fixture_pdf,
                context=context(5), copyright_scope="test",
            )
        self.assertEqual("PATH_NOT_AUTHORIZED", error.exception.code)

    def test_invalid_pdf_gets_receipt_without_moving_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "broken.pdf"
            source.write_text("not a pdf", encoding="utf-8")
            result = MaterialImporter(MaterialCatalog(), (root,)).import_with_quarantine_receipt(
                source, context=context(6), copyright_scope="test", quarantine_directory=root / "quarantine"
            )
            self.assertEqual("error", result["status"])
            receipt = json.loads(Path(result["data"]["quarantine_receipt"]).read_text(encoding="utf-8"))
            self.assertEqual("PDF_PARSE_FAILED", receipt["error_code"])
            self.assertFalse(receipt["source_moved"])
            self.assertTrue(source.exists())
            replay = MaterialImporter(MaterialCatalog(), (root,)).import_with_quarantine_receipt(
                source, context=context(6), copyright_scope="test", quarantine_directory=root / "quarantine"
            )
            self.assertEqual(result["data"]["quarantine_receipt"], replay["data"]["quarantine_receipt"])

    def test_timestamped_subtitle_search(self) -> None:
        catalog = MaterialCatalog()
        fixture_root = ROOT / "tests" / "fixtures"
        result = MaterialImporter(catalog, (fixture_root,)).import_file(
            fixture_root / "sample.zh.srt", context=context(7), copyright_scope="project_test_fixture",
            video_name="05-质量属性.mp4",
        )
        self.assertEqual(2, result["data"]["segment_count"])
        match = MaterialSearch(catalog).search("心跳 检测", media_type="transcript")[0]
        self.assertEqual(4.0, match["start_seconds"])
        self.assertEqual(7.0, match["end_seconds"])
        self.assertIn("心跳", match["snippet"])
        self.assertEqual("05-质量属性.mp4@00:00:04-00:00:07", match["open_target"])

    def test_clip_subtitle_offset_preserves_original_video_timeline(self) -> None:
        catalog = MaterialCatalog()
        fixture_root = ROOT / "tests" / "fixtures"
        result = MaterialImporter(catalog, (fixture_root,)).import_file(
            fixture_root / "sample.zh.srt",
            context=context(8),
            copyright_scope="project_test_fixture",
            video_name="00-导学课.mp4",
            subtitle_offset_seconds=600,
            video_source_id="sha256:" + "a" * 64,
            transcript_confidence=0.7,
        )
        self.assertEqual(2, result["data"]["segment_count"])
        match = MaterialSearch(catalog).search("心跳 检测", media_type="transcript")[0]
        self.assertEqual(604.0, match["start_seconds"])
        self.assertEqual(607.0, match["end_seconds"])
        self.assertEqual("00-导学课.mp4@00:10:04-00:10:07", match["open_target"])
        self.assertEqual(0.7, match["confidence"])
        self.assertTrue(match["citation_anchor"].startswith("video:sha256:" + "a" * 64))

        with self.assertRaises(MaterialError) as error:
            MaterialImporter(MaterialCatalog(), (fixture_root,)).import_file(
                fixture_root / "sample.zh.srt",
                context=context(9),
                copyright_scope="project_test_fixture",
                video_name="00-导学课.mp4",
                subtitle_offset_seconds=-1,
            )
        self.assertEqual("INVALID_SUBTITLE_OFFSET", error.exception.code)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg is required")
    def test_video_probe_and_audio_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            video = root / "synthetic.mp4"
            audio = root / "audio.wav"
            subprocess.run([
                shutil.which("ffmpeg"), "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                "color=c=black:s=160x120:d=1", "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
                "-shortest", "-c:v", "libx264", "-c:a", "aac", "-y", str(video),
            ], check=True)
            metadata = probe_video(video)
            self.assertGreaterEqual(metadata["duration_seconds"], 1.0)
            audio_context = context(10)
            extract_audio(video, audio, context=audio_context)
            self.assertTrue(audio.exists())
            self.assertGreater(audio.stat().st_size, 1000)
            self.assertTrue(audio.with_name("audio.wav.audit.json").exists())
            self.assertEqual(audio, extract_audio(video, audio, context=audio_context))
            clip = root / "clip.wav"
            extract_audio_clip(
                video,
                clip,
                start_seconds=0.25,
                duration_seconds=0.5,
                context=context(11),
            )
            self.assertTrue(clip.exists())
            self.assertGreater(clip.stat().st_size, 1000)
            with self.assertRaises(MaterialError):
                extract_audio_clip(
                    video,
                    root / "too-long.wav",
                    start_seconds=0,
                    duration_seconds=901,
                    context=context(12),
                )

    def test_transcription_uses_fixed_arguments_and_audited_idempotency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio = root / "clip.wav"
            model = root / "model.bin"
            audio.write_bytes(b"audiodata")
            model.write_bytes(b"modeldata")

            def fake_run(arguments, **kwargs):
                self.assertIsInstance(arguments, list)
                self.assertNotIn("shell", kwargs)
                output_base = Path(arguments[arguments.index("--output-file") + 1])
                output_base.with_suffix(".srt").write_text(
                    "1\n00:00:01,000 --> 00:00:02,000\n本地转写测试\n",
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(arguments, 0, "", "")

            write_context = context(13)
            with patch("architectpass_materials.video.shutil.which", return_value="/usr/local/bin/whisper-cli"), patch(
                "architectpass_materials.video.subprocess.run", side_effect=fake_run
            ) as run:
                subtitle = transcribe_audio_whisper_cpp(
                    audio,
                    model=model,
                    output_directory=root / "transcripts",
                    output_stem="clip",
                    use_gpu=False,
                    context=write_context,
                )
                self.assertEqual(1, run.call_count)
                self.assertIn("--no-gpu", run.call_args.args[0])
                self.assertTrue(subtitle.with_name("clip.srt.audit.json").exists())
                replay = transcribe_audio_whisper_cpp(
                    audio,
                    model=model,
                    output_directory=root / "transcripts",
                    output_stem="clip",
                    use_gpu=False,
                    context=write_context,
                )
                self.assertEqual(subtitle, replay)
                self.assertEqual(1, run.call_count)


if __name__ == "__main__":
    unittest.main()
