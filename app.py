import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

from chatpdf.config import UPLOAD_FOLDER
from chatpdf.ingest import ingest_pdf
from chatpdf.query import answer_query

load_dotenv()

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST", "GET"])
def chat():
    if request.method != "POST":
        return render_template("chat.html")

    if "chatPdfFile" not in request.files:
        return redirect(url_for("index"))

    file = request.files["chatPdfFile"]
    if not file or file.filename == "" or not allowed_file(file.filename):
        return redirect(url_for("index"))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    safe_name = secure_filename(file.filename)
    doc_id = f"{int(time.time())}_{safe_name.rsplit('.', 1)[0]}"
    file_path = os.path.join(UPLOAD_FOLDER, f"{doc_id}.pdf")

    try:
        file.save(file_path)
        ingest_pdf(file_path, doc_id)
    except Exception as exc:
        app.logger.exception("Failed to ingest PDF")
        if os.path.isfile(file_path):
            os.unlink(file_path)
        return render_template("index.html", error=str(exc)), 400

    return render_template("chat.html", doc_id=doc_id)


@app.route("/api/chat", methods=["POST"])
def pdfchat():
    if not request.is_json:
        return jsonify({"error": "Expected application/json"}), 400

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    doc_id = data.get("doc_id")

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
    if not doc_id:
        return jsonify({"error": "Missing 'doc_id' in request body"}), 400

    try:
        text = answer_query(prompt, doc_id)
        return jsonify({"text": text}), 200
    except (ValueError, FileNotFoundError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Chat failed")
        return jsonify({"error": "Failed to generate a response. Please try again."}), 500


if __name__ == "__main__":
    # threaded=True so one blocked LLM call does not stall every other request
    app.run(threaded=True)
