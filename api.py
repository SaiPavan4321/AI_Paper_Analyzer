from flask import Flask, request, jsonify
import os
import tempfile
import threading

from nlp_modules.document_ingestion import run_document_ingestion
from nlp_modules.ai_summarization import ai_summarization_pipeline
from nlp_modules.insight_extraction import insight_extraction_pipeline
from nlp_modules.text_preprocessing import text_preprocessing_pipeline

app = Flask(__name__)

# 🔒 GLOBAL LOCK (CRITICAL FIX)
nlp_lock = threading.Lock()


def save_temp_pdf(uploaded_file):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp.write(uploaded_file.read())
    temp.close()
    return temp.name


@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        with nlp_lock:   # 🔒 lock
            file = request.files["file"]
            path = save_temp_pdf(file)
            summary = ai_summarization_pipeline(path)
            os.remove(path)
            return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/insights", methods=["POST"])
def insights():
    try:
        with nlp_lock:   # 🔒 lock
            file = request.files["file"]
            path = save_temp_pdf(file)
            result = insight_extraction_pipeline(path)
            os.remove(path)
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/preprocess", methods=["POST"])
def preprocess():
    try:
        with nlp_lock:   # 🔒 lock
            file = request.files["file"]
            path = save_temp_pdf(file)
            output = text_preprocessing_pipeline(path)
            os.remove(path)
            return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
