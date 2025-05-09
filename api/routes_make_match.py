from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
from src.matchmaker_engine.matching_engine import MatchingEngine

make_match_bp = Blueprint("make_match", __name__)

@make_match_bp.route("/make_match", methods=["POST"])
@swag_from("docs/make_match.yml")
def make_match():
    data = request.get_json()
    resumeJSON = data.get("resume_json")
    jdJSON = data.get("jd_json")
    if not resumeJSON or not jdJSON or not isinstance(resumeJSON, dict) or not isinstance(jdJSON, dict):
        return jsonify({"error": "Invalid input or missing input"}), 400
    try:
        matchMaker = MatchingEngine()
        matchMaker.resumeText = matchMaker.jdText = "Set to None"
        matchMaker.resume_json = resumeJSON
        matchMaker.jd_json = jdJSON
        matchReport = matchMaker.getMatch()
        return jsonify({'match_report': matchReport}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the input"}), 500

    
    



