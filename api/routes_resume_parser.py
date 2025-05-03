from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from src.resume_ocr.resume_ocr import ResumeOCR

resume_parser_bp = Blueprint("resume_parser", __name__)

@resume_parser_bp.route("/parse_resume", methods=["POST"])
@swag_from("docs/parse_resume.yml")
def parse_resume():
    file = request.files.get("resume_file")
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid input or missing file"}), 400
    try:
        pdfBytes = file.read()
        resume_ocr = ResumeOCR()
        resume_ocr.setInputs(pdfPath=None, pdfBytes=pdfBytes)
        text = resume_ocr.extractText()
        resume_ocr.resetOCR()
        return jsonify({'resume_text' : text}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the file"}), 500
    
    
        


