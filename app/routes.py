from flask import Blueprint, request, jsonify
from app.services import Processing, insert_video_status, update_video_status

video_bp = Blueprint('video', __name__)

@video_bp.route('/process_event', methods=['POST'])
async def process_event():
    try:

        data = request.get_json()
        event_id = data.get('event_id')

        if not event_id:
            return jsonify({"error": "event_id are required"}), 400

        analisys_id = await insert_video_status(event_id, 0)
        print(f"Record created with analisys_id: {analisys_id}")

        print("Start processing...")
        processing = Processing(event_id)

        try:
            results = await processing.process_event()
            await update_video_status(analisys_id, 1)
            print("End processing successfully.")
            return jsonify({"results": results}), 200

        except Exception as e:
            await update_video_status(analisys_id, 2)
            print(f"Error during processing: {e}")
            return jsonify({"error": "Processing failed", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500