# Flask backend route
from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from src.utils import llm_config_loader 

config_bp = Blueprint("config", __name__)


@config_bp.route("/get_model_config", methods=["GET"])
@swag_from("docs/fetch_config.yml")
def get_model_config():
    config = llm_config_loader.Config()
    modelConfig = config.MODEL_NAMES
    return jsonify(modelConfig), 200
