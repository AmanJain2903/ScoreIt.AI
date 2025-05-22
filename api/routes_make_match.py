from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from src.matchmaker_engine.matching_engine import MatchingEngine
import json
import gc

make_match_bp = Blueprint("make_match", __name__)

@make_match_bp.route("/make_match", methods=["POST"])
@swag_from("docs/make_match.yml")
def make_match():
    data = request.get_json()
    resumeJSON = data.get("resume_json")
    jdJSON = data.get("jd_json")
    if not resumeJSON or not jdJSON or not isinstance(resumeJSON, dict) or not isinstance(jdJSON, dict):
        try:
            resumeJSON = json.loads(resumeJSON)
            jdJSON = json.loads(jdJSON)
        except Exception:
            return jsonify({"error": "Invalid input or missing input"}), 400
    try:
        matchMaker = MatchingEngine()
        matchMaker.resume_json = resumeJSON
        matchMaker.jd_json = jdJSON
        matchReport = matchMaker.getMatch()
        return jsonify({'match_report': matchReport}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the input"}), 500
    finally:
        try:
            if data: del data
            if resumeJSON: del resumeJSON
            if jdJSON: del jdJSON
            if matchMaker: del matchMaker
            if matchReport: del matchReport
        except Exception:
            pass
        gc.collect()

    
    



