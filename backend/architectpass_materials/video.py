from __future__ import annotations

import json
import hashlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .errors import MaterialError
from .models import MaterialContext
from .paths import safe_output


def probe_video(path: Path) -> dict[str, object]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise MaterialError("FFPROBE_UNAVAILABLE", "ffprobe is not installed")
    process = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration,size", "-show_streams", "-of", "json", str(path)],
        capture_output=True, text=True, check=False,
    )
    if process.returncode != 0:
        raise MaterialError("VIDEO_PROBE_FAILED", process.stderr.strip() or "ffprobe failed")
    data = json.loads(process.stdout)
    return {
        "duration_seconds": float(data["format"]["duration"]),
        "size_bytes": int(data["format"]["size"]),
        "streams": [{"codec_type": stream.get("codec_type"), "codec_name": stream.get("codec_name")} for stream in data.get("streams", [])],
    }


def extract_audio(path: Path, output: Path, *, context: MaterialContext) -> Path:
    parameters = {"channels": 1, "sample_rate": 16000}
    if _prepare_derived_write(path, output, "extract_audio", parameters, context):
        return output
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MaterialError("FFMPEG_UNAVAILABLE", "ffmpeg is not installed")
    process = subprocess.run(
        [ffmpeg, "-nostdin", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", str(output)],
        capture_output=True, text=True, check=False,
    )
    if process.returncode != 0:
        raise MaterialError("AUDIO_EXTRACTION_FAILED", process.stderr.strip() or "ffmpeg failed")
    _finish_derived_write(path, output, "extract_audio", parameters, context)
    return output


def extract_audio_clip(
    path: Path,
    output: Path,
    *,
    start_seconds: float,
    duration_seconds: float,
    context: MaterialContext,
) -> Path:
    """Extract a bounded local clip; useful for targeted review and acceptance probes."""
    if start_seconds < 0 or duration_seconds <= 0 or duration_seconds > 900:
        raise MaterialError(
            "CLIP_RANGE_NOT_ALLOWED",
            "start must be non-negative and duration must be between 0 and 900 seconds",
        )
    parameters = {
        "start_seconds": start_seconds,
        "duration_seconds": duration_seconds,
        "channels": 1,
        "sample_rate": 16000,
    }
    if _prepare_derived_write(path, output, "extract_audio_clip", parameters, context):
        return output
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise MaterialError("FFMPEG_UNAVAILABLE", "ffmpeg is not installed")
    process = subprocess.run(
        [
            ffmpeg, "-nostdin", "-v", "error",
            "-ss", f"{start_seconds:.3f}", "-i", str(path),
            "-t", f"{duration_seconds:.3f}", "-vn", "-ac", "1", "-ar", "16000", str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise MaterialError("AUDIO_EXTRACTION_FAILED", process.stderr.strip() or "ffmpeg failed")
    _finish_derived_write(path, output, "extract_audio_clip", parameters, context)
    return output


def transcribe_audio_whisper_cpp(
    audio: Path,
    *,
    model: Path,
    output_directory: Path,
    output_stem: str,
    language: str = "zh",
    threads: int = 8,
    use_gpu: bool = True,
    context: MaterialContext,
) -> Path:
    """Run local whisper.cpp with fixed, non-shell arguments and emit timestamped SRT."""
    whisper_cli = shutil.which("whisper-cli")
    if not whisper_cli:
        raise MaterialError("WHISPER_CPP_UNAVAILABLE", "whisper-cli is not installed")
    if not audio.is_file():
        raise MaterialError("AUDIO_NOT_FOUND", "audio source does not exist")
    if not model.is_file():
        raise MaterialError("WHISPER_MODEL_NOT_FOUND", "whisper.cpp model does not exist")
    if language not in {"zh", "auto"}:
        raise MaterialError("LANGUAGE_NOT_ALLOWED", "only zh or auto is allowed")
    if threads < 1 or threads > 16:
        raise MaterialError("THREAD_COUNT_NOT_ALLOWED", "threads must be between 1 and 16")
    output_base = safe_output(output_directory, output_stem)
    subtitle = output_base.with_suffix(".srt")
    parameters = {
        "model_sha256": _sha256(model),
        "language": language,
        "threads": threads,
        "use_gpu": use_gpu,
        "format": "srt",
    }
    if _prepare_derived_write(audio, subtitle, "transcribe_whisper_cpp", parameters, context):
        return subtitle
    arguments = [
        whisper_cli,
        "-m", str(model),
        "-f", str(audio),
        "-l", language,
        "-t", str(threads),
        "--output-srt",
        "--output-file", str(output_base),
        "--no-prints",
    ]
    if not use_gpu:
        arguments.append("--no-gpu")
    process = subprocess.run(
        arguments,
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0:
        raise MaterialError("TRANSCRIPTION_FAILED", process.stderr.strip() or "whisper-cli failed")
    if not subtitle.is_file() or not subtitle.read_text(encoding="utf-8", errors="replace").strip():
        raise MaterialError("TRANSCRIPTION_OUTPUT_MISSING", "whisper-cli did not create a non-empty SRT")
    _finish_derived_write(audio, subtitle, "transcribe_whisper_cpp", parameters, context)
    return subtitle


def _prepare_derived_write(
    source: Path,
    output: Path,
    operation: str,
    parameters: dict[str, object],
    context: MaterialContext,
) -> bool:
    context.validate()
    if not source.is_file():
        raise MaterialError("SOURCE_NOT_FOUND", "derived material source does not exist")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = _receipt_path(output)
    fingerprint = _write_fingerprint(source, operation, parameters)
    if output.exists() or receipt.exists():
        if output.is_file() and receipt.is_file():
            prior = json.loads(receipt.read_text(encoding="utf-8"))
            if prior.get("request_id") == context.request_id and prior.get("fingerprint") == fingerprint:
                return True
        raise MaterialError("DERIVED_OUTPUT_CONFLICT", "derived output already exists with a different or incomplete audit")
    return False


def _finish_derived_write(
    source: Path,
    output: Path,
    operation: str,
    parameters: dict[str, object],
    context: MaterialContext,
) -> None:
    if not output.is_file():
        raise MaterialError("DERIVED_OUTPUT_MISSING", "processor did not create its expected output")
    receipt = {
        "request_id": context.request_id,
        "audit_id": context.audit_id,
        "actor": context.actor,
        "operation": operation,
        "fingerprint": _write_fingerprint(source, operation, parameters),
        "source_filename": source.name,
        "source_sha256": _sha256(source),
        "output_filename": output.name,
        "output_sha256": _sha256(output),
        "parameters": parameters,
        "success": True,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    _receipt_path(output).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _receipt_path(output: Path) -> Path:
    return output.with_name(f"{output.name}.audit.json")


def _write_fingerprint(source: Path, operation: str, parameters: dict[str, object]) -> str:
    payload = {
        "source_sha256": _sha256(source),
        "operation": operation,
        "parameters": parameters,
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
