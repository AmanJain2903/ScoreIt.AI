from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
from src.resume_extractor_agent.resume_agent import ResumeAgent
import gc
import time

resume_extractor_bp = Blueprint("resume_extracter", __name__)

@resume_extractor_bp.route("/extract_resume", methods=["POST"])
@swag_from("docs/extract_resume.yml")
def extract_resume():
    start = time.time()
    print(f"⚙️  Starting resume extraction...")
    text = request.form.get("resume_text")
    modelID = int(request.form.get("model_id"))
    if not text:
        return jsonify({"error": "Invalid input or missing text"}), 400
    try:
        resumeAgent = ResumeAgent(
            apiKey=os.getenv('OPENROUTER_API_KEY'),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True,
            modelID=modelID
        )
        resumeAgent.setUserPrompt(text)
        output = resumeAgent.getJsonOutput()
        resumeAgent.deleteAgent()
        return jsonify({'resume_entites': output}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the text"}), 500
    finally:
        end = time.time()
        print(f"✅ Resume extraction completed in {end - start:.2f}s")
        try:
            if text: del text
            if resumeAgent: del resumeAgent
            if start: del start
            if end: del end
        except Exception:
            pass
        gc.collect()




    
    
        


