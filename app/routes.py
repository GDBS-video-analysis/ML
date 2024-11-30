# Запросы POST и GET

from flask import Blueprint, request, jsonify
from app.model import process_video_file, load_results
import os

from app.model_debug import process_video_file_debug

video_bp = Blueprint('video', __name__)

@video_bp.route('/process_video', methods=['POST'])
def process_video():
    try:
        video_path = request.json.get("video_path")
        biometry_path = request.json.get("biometry_path")

        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Video file not found"}), 400

        if not os.path.exists(biometry_path):
            return jsonify({"error": f"Passed path {biometry_path} does not exist!"}), 400

        results = process_video_file_debug(video_path, biometry_path)
        return jsonify({"message": "success", "results": results})
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_bp.route('/results', methods=['GET'])
def get_results():
    try:
        results = load_results()
        return jsonify(results)
    except FileNotFoundError:
        return jsonify({"error": "No results found. Process a video first."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500