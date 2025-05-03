from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent

jd_extractor_bp = Blueprint("jd_extracter", __name__)

@jd_extractor_bp.route("/extract_jd", methods=["POST"])
@swag_from("docs/extract_jd.yml")
def extract_jd():
    text = request.form.get("jd_text")
    if not text:
        return jsonify({"error": "Invalid input or missing text"}), 400
    try:
        jdAgent = JobDescriptionAgent(
            apiKey=os.getenv('OPENROUTER_API_KEY'),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True
        )
        jdAgent.setUserPrompt(text)
        output = jdAgent.getJsonOutput()
        jdAgent.deleteAgent()
        return jsonify({'jd_entites': output}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the text"}), 500

    
    
        


