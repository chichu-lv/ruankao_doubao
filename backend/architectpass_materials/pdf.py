from __future__ import annotations

import csv
import hashlib
import io
import shutil
import subprocess
import tempfile
from pathlib import Path

import pdfplumber

from .errors import MaterialError
from .models import Segment


def extract_pdf_pages(path: Path, resource_id: str) -> tuple[list[Segment], dict[str, object]]:
    segments: list[Segment] = []
    try:
        with pdfplumber.open(path) as pdf:
            metadata = {"page_count": len(pdf.pages), "pdf_metadata": dict(pdf.metadata or {})}
            for page_number, page in enumerate(pdf.pages, start=1):
                text = (page.extract_text(x_tolerance=2, y_tolerance=3) or "").strip()
                needs_ocr = _needs_ocr(text)
                segment_id = hashlib.sha256(f"{resource_id}:page:{page_number}".encode()).hexdigest()[:24]
                segments.append(Segment(
                    segment_id=segment_id,
                    resource_id=resource_id,
                    filename=path.name,
                    section=_first_heading(text),
                    text=text,
                    confidence=0.35 if needs_ocr else 1.0,
                    citation_anchor=f"pdf:{resource_id}#page={page_number}",
                    open_target=f"{path}#page={page_number}",
                    page=page_number,
                    ocr=False,
                ))
            metadata["ocr_candidate_pages"] = [item.page for item in segments if item.confidence < 1]
            return segments, metadata
    except Exception as error:
        raise MaterialError("PDF_PARSE_FAILED", f"PDF parse failed: {type(error).__name__}: {error}") from error


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:120]
    return None


def _needs_ocr(text: str) -> bool:
    compact = "".join(text.split())
    if len(compact) < 12:
        return True
    cjk = sum("\u4e00" <= character <= "\u9fff" for character in compact)
    # ArchitectPass course PDFs are Chinese. Sparse/no CJK after extraction usually
    # means an image page or an unusable embedded-font mapping, even when numbers
    # and URLs inflate the raw character count.
    return cjk < 4 or cjk / len(compact) < 0.05


def apply_local_ocr(
    path: Path,
    segments: list[Segment],
    page_numbers: tuple[int, ...],
    *,
    tessdata_directory: Path | None = None,
    language: str = "chi_sim",
) -> list[Segment]:
    """OCR only explicitly requested pages that ordinary extraction marked unusable."""
    if not page_numbers:
        return segments
    pdftoppm = shutil.which("pdftoppm")
    tesseract = shutil.which("tesseract")
    if not pdftoppm or not tesseract:
        raise MaterialError("OCR_ENGINE_UNAVAILABLE", "pdftoppm and tesseract are required")
    by_page = {segment.page: segment for segment in segments}
    requested = set(page_numbers)
    if len(requested) != len(page_numbers) or any(page is None or page < 1 for page in requested):
        raise MaterialError("INVALID_OCR_PAGE", "OCR pages must be unique positive integers")
    for page_number in requested:
        segment = by_page.get(page_number)
        if segment is None:
            raise MaterialError("INVALID_OCR_PAGE", f"PDF page does not exist: {page_number}")
        if segment.confidence >= 1:
            raise MaterialError("OCR_NOT_NEEDED", f"ordinary extraction is usable on page {page_number}")
    with tempfile.TemporaryDirectory(prefix="architectpass-ocr-") as directory:
        work = Path(directory)
        for page_number in sorted(requested):
            image_base = work / f"page-{page_number}"
            render = subprocess.run(
                [
                    pdftoppm, "-f", str(page_number), "-l", str(page_number),
                    "-singlefile", "-png", "-r", "220", str(path), str(image_base),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if render.returncode != 0:
                raise MaterialError("OCR_RENDER_FAILED", render.stderr.strip() or "pdftoppm failed")
            image_path = image_base.with_suffix(".png")
            arguments = [
                tesseract, str(image_path), "stdout", "-l", language,
                "--oem", "1", "--psm", "6", "-c", "tessedit_create_tsv=1",
            ]
            if tessdata_directory is not None:
                arguments[3:3] = ["--tessdata-dir", str(tessdata_directory)]
            ocr = subprocess.run(arguments, capture_output=True, text=True, check=False)
            if ocr.returncode != 0:
                raise MaterialError("OCR_FAILED", ocr.stderr.strip() or "tesseract failed")
            text, confidence = _text_from_tsv(ocr.stdout)
            if not text.strip():
                raise MaterialError("OCR_EMPTY", f"OCR produced no text on page {page_number}")
            segment = by_page[page_number]
            assert segment is not None
            segment.text = text
            segment.section = _first_heading(text)
            segment.confidence = confidence
            segment.ocr = True
    return segments


def _text_from_tsv(value: str) -> tuple[str, float]:
    reader = csv.DictReader(io.StringIO(value), delimiter="\t")
    lines: dict[tuple[str, str, str, str], list[str]] = {}
    confidences: list[float] = []
    for row in reader:
        word = (row.get("text") or "").strip()
        if not word:
            continue
        try:
            confidence = float(row.get("conf") or -1)
        except ValueError:
            continue
        if confidence < 0:
            continue
        key = tuple(row.get(name, "") for name in ("page_num", "block_num", "par_num", "line_num"))
        lines.setdefault(key, []).append(word)
        confidences.append(confidence)
    text = "\n".join(_join_ocr_words(words) for words in lines.values())
    average = sum(confidences) / len(confidences) / 100 if confidences else 0.0
    return text, round(average, 4)


def _join_ocr_words(words: list[str]) -> str:
    line = ""
    for word in words:
        if line and not (_is_cjk(line[-1]) and _is_cjk(word[0])):
            line += " "
        line += word
    return line


def _is_cjk(character: str) -> bool:
    return "\u4e00" <= character <= "\u9fff"
