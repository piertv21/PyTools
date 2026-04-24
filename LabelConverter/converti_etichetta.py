"""
converti_etichetta.py
─────────────────────
Looks for a PDF in the same folder whose name matches the pattern:
    etichetta<uuid>.pdf
    e.g. etichetta24e68007-6798-4061-9f86-36125cb5a391.pdf

Generates a printable A4 PDF with the shipping label scaled down and centred.

Dependency:
    pip install pypdf
"""

import sys
import re
import glob
from pathlib import Path
from pypdf import PdfReader, PdfWriter, PageObject, Transformation


# ── A4 dimensions in points (1 pt = 1/72 inch) ─────────────────────────────
A4_W = 595.28   # 210 mm
A4_H = 841.89   # 297 mm

# The label will occupy at most this fraction of the A4 page
MAX_SCALE = 0.75

# Top margin from the upper edge of the A4 page (in points)
MARGIN_TOP = 40


def find_etichetta(folder: Path) -> Path:
    """Find the first PDF matching the pattern etichetta<uuid>.pdf."""
    pattern = str(folder / "etichetta*.pdf")
    uuid_re = re.compile(
        r"etichetta[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
        r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.pdf$"
    )
    candidates = [Path(p) for p in glob.glob(pattern)]
    matched = [p for p in candidates if uuid_re.search(p.name)]

    if not matched:
        if candidates:
            print(f"[WARN] No valid UUID found; using: {candidates[0].name}")
            return candidates[0]
        raise FileNotFoundError(
            f"No 'etichetta<uuid>.pdf' file found in: {folder}"
        )

    if len(matched) > 1:
        print(f"[WARN] Found {len(matched)} files; using: {matched[0].name}")

    return matched[0]


def build_a4_pdf(input_path: Path, output_path: Path, max_scale: float = MAX_SCALE):
    reader = PdfReader(str(input_path))
    src_page = reader.pages[0]

    src_w = float(src_page.mediabox.width)
    src_h = float(src_page.mediabox.height)

    # Uniform scale that keeps the label within max_scale of the A4 page.
    # Capped at 1.0 so the label is never upscaled if it is already small.
    scale = min(
        (A4_W * max_scale) / src_w,
        (A4_H * max_scale) / src_h,
        1.0,
    )

    scaled_w = src_w * scale
    scaled_h = src_h * scale

    # Horizontally centred; positioned near the top with a small margin
    tx = (A4_W - scaled_w) / 2
    ty = A4_H - MARGIN_TOP - scaled_h

    # Create a blank A4 page and overlay the transformed label
    writer = PdfWriter()
    a4_page = PageObject.create_blank_page(width=A4_W, height=A4_H)

    transform = Transformation().scale(scale, scale).translate(tx, ty)
    a4_page.merge_transformed_page(src_page, transform)

    writer.add_page(a4_page)

    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"[OK] Output file  : {output_path.name}")
    print(f"     Original size : {src_w:.0f} x {src_h:.0f} pt")
    print(f"     Scale applied : {scale:.1%} -> {scaled_w:.0f} x {scaled_h:.0f} pt on A4")


def main():
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1]).resolve()
    else:
        folder = Path(__file__).resolve().parent

    print(f"Search folder : {folder}")

    input_pdf  = find_etichetta(folder)
    print(f"File found    : {input_pdf.name}")

    output_pdf = folder / (input_pdf.stem + "_A4.pdf")
    build_a4_pdf(input_pdf, output_pdf)


if __name__ == "__main__":
    main()
