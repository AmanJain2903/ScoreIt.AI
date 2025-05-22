from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
from src.jd_extractor_agent.jd_agent import JobDescriptionAgent
import gc
import time

jd_extractor_bp = Blueprint("jd_extracter", __name__)

@jd_extractor_bp.route("/extract_jd", methods=["POST"])
@swag_from("docs/extract_jd.yml")
def extract_jd():
    start = time.time()
    print(f"⚙️  Starting JD extraction...")
    text = request.form.get("jd_text")
    modelID = int(request.form.get("model_id"))
    if not text:
        return jsonify({"error": "Invalid input or missing text"}), 400
    try:
        jdAgent = JobDescriptionAgent(
            apiKey=os.getenv('OPENROUTER_API_KEY'),
            modelName=None,
            systemPrompt=None,
            useDefaultModelIfNone=True,
            useDefaultSystemPromptIfNone=True,
            modelID=modelID
        )
        jdAgent.setUserPrompt(text)
        output = jdAgent.getJsonOutput()
        jdAgent.deleteAgent()
        return jsonify({'jd_entites': output}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the text"}), 500
    finally:
        end = time.time()
        print(f"✅ JD extraction completed in {end - start:.2f}s")
        try:
            if text: del text
            if jdAgent: del jdAgent
            if start: del start
            if end: del end
        except Exception:
            pass
        gc.collect()
    



    
    
        


