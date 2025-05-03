from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from urllib.parse import urlparse
from src.jd_scraper.jd_scraper import JobDescriptionScraper

jd_parser_bp = Blueprint("jd_parser", __name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@jd_parser_bp.route("/parse_jd", methods=["POST"])
@swag_from("docs/parse_jd.yml")
def parse_jd():
    link = request.form.get("jd_link")
    if not link or not is_valid_url(link):
        return jsonify({"error": "Invalid input or missing link"}), 400
    try:
        scraper = JobDescriptionScraper()
        scraper.setInputs(link)
        data = scraper.extractJobDescription()
        return jsonify({'jd_text':data}), 200
    except Exception:
        return jsonify({"error": "Internal error while processing the link"}), 500

    
    
        


