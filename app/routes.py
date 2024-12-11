from flask import Blueprint, request, jsonify
from app.services import Processing

video_bp = Blueprint('video', __name__)

@video_bp.route('/process_event', methods=['POST'])
async def process_event():
    try:
        # Получаем event_id из данных POST-запроса
        data = request.get_json()
        event_id = data.get('event_id')

        if not event_id:
            return jsonify({"error": "event_id is required"}), 400
        

        print("start processing...")
        # Создаем экземпляр класса Processing
        processing = Processing(event_id)
        
        # Запускаем обработку события
        results = await processing.process_event()
        print("end processing successfully.")
        # Возвращаем результат в формате JSON
        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500