"""
main.py – Flask web server for the Label Converter tool.

Serves the upload page and processes shipping-label PDFs into
printable A4 PDFs using converti_etichetta.build_a4_pdf().

Authentication is enforced via APP_PASSWORD (environment variable).
"""

import os
import uuid
import shutil
import secrets
from pathlib import Path
from functools import wraps

from dotenv import load_dotenv
load_dotenv()


from flask import (
    Flask, request, send_file, render_template,
    jsonify, redirect, url_for, session, flash,
)

from converti_etichetta import build_a4_pdf

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

APP_PASSWORD = os.getenv("APP_PASSWORD", "")

UPLOAD_DIR = Path("/app/uploads") if os.getenv("RENDER") else Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Auth helpers ─────────────────────────────────────────────────────────────
def login_required(f):
    """Decorator that redirects unauthenticated users to the login page."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    """Show login form and handle authentication."""
    if session.get("authenticated"):
        return redirect(url_for("index"))

    if request.method == "POST":
        password = request.form.get("password", "")

        if not APP_PASSWORD:
            flash("Autenticazione non configurata sul server.", "error")
            return render_template("login.html"), 500

        if secrets.compare_digest(password, APP_PASSWORD):
            session["authenticated"] = True
            session.permanent = True
            return redirect(url_for("index"))
        else:
            flash("Password errata.", "error")
            return render_template("login.html"), 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    """Serve the main upload page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
@login_required
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