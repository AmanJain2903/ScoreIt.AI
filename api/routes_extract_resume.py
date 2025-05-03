from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
from src.resume_extractor_agent.resume_agent import ResumeAgent

resume_extractor_bp = Blueprint("resume_extracter", __name__)

@resume_extractor_bp.route("/extract_resume", methods=["POST"])
@swag_from("docs/extract_resume.yml")
def extract_resume():
    text = request.form.get("resume_text")
    if not text:
        return jsonify({"error": "Invalid input or missing text"}), 400
    try:
        resumeAgent = ResumeAgent(
            apiKey=os.getenv('OPENROUTER_API_KEY'),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True
        )
        resumeAgent.setUserPrompt(text)
        output = resumeAgent.getJsonOutput()
        resumeAgent.deleteAgent()
        return jsonify({'resume_entites': output}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the text"}), 500

    
    
        


