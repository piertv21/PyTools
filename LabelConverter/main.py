"""
main.py – Flask web server for the Label Converter tool.

Serves the upload page and processes shipping-label PDFs into
printable A4 PDFs using converti_etichetta.build_a4_pdf().
"""

import os
import uuid
import shutil
from pathlib import Path

from flask import Flask, request, send_file, render_template, jsonify

from converti_etichetta import build_a4_pdf

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")

UPLOAD_DIR = Path("/app/uploads") if os.getenv("RENDER") else Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def index():
    """Serve the main upload page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Accept a PDF, convert it to A4 and return the result."""
    if "file" not in request.files:
        return jsonify({"error": "Nessun file inviato."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nessun file selezionato."}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "È consentito solo il formato PDF."}), 400

    # Create a unique working directory so concurrent requests don't collide
    job_id = uuid.uuid4().hex
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        input_path = job_dir / file.filename
        file.save(str(input_path))

        output_name = input_path.stem + "_A4.pdf"
        output_path = job_dir / output_name

        build_a4_pdf(input_path, output_path)

        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=output_name,
            mimetype="application/pdf",
        )
    finally:
        # Clean up temporary files after the response is sent
        shutil.rmtree(job_dir, ignore_errors=True)


@app.route("/health")
def health():
    """Health-check endpoint used by Render."""
    return jsonify({"status": "ok"})


# ── Local development server ─────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)