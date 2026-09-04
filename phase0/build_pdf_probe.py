from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "output" / "pdf" / "phase0-local-file-probe.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = A4
    pdf = canvas.Canvas(str(output), pagesize=A4)
    pdf.setTitle("ArchitectPass Phase 0 Local File Probe")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, page_height - 96, "ArchitectPass Phase 0 Local File Probe")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(72, page_height - 132, "Marker: ARCHITECTPASS_LOCAL_FILE_PROBE_20260903")
    pdf.drawString(72, page_height - 154, "Purpose: verify authorized local PDF reading in Doubao.")
    pdf.drawString(72, page_height - 176, "Contains no personal, account, course, or confidential data.")
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(72, 54, "Generated for Phase 0 capability audit - 2026-09-03")
    pdf.save()


if __name__ == "__main__":
    main()
