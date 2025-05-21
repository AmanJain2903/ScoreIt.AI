from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from api.routes_resume_parser import resume_parser_bp
from api.routes_jd_parser import jd_parser_bp
from api.routes_extract_resume import resume_extractor_bp
from api.routes_extract_jd import jd_extractor_bp
from api.routes_make_match import make_match_bp
from api.routes_auth import auth_bp
from api.routes_history import history_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    Swagger(app)

    @app.route("/")
    def home():
        return "✅ ScoreIt.AI backend is running!"

    app.register_blueprint(resume_parser_bp, url_prefix="/")
    app.register_blueprint(jd_parser_bp, url_prefix="/")
    app.register_blueprint(resume_extractor_bp, url_prefix="/")
    app.register_blueprint(jd_extractor_bp, url_prefix="/")
    app.register_blueprint(make_match_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(history_bp, url_prefix="/")

    return app