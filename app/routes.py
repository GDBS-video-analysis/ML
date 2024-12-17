from app.services.event_queue import event_queue
from flask import Blueprint, request, jsonify
from app.services import insert_video_status

video_bp = Blueprint('video', __name__)

@video_bp.route('/process_event', methods=['POST'])
async def process_event_route():
    try:
        data = request.get_json()
        event_id = data.get('event_id')

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400
        
        # Ставим в очередь
        cur_status = await insert_video_status(event_id=event_id, status=0)

        event_queue.put((event_id, cur_status))

        return jsonify({"message": "record added to queue"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500