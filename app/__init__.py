import asyncio
from datetime import time
from flask import Flask
import threading
from app.services.event_queue import event_queue
from app.routes import video_bp
from app.services.processing import process_event
from app.services import insert_video_status, update_video_status

async def process_event_background():
    print("start processing thread.")
    while True:
        event_data = event_queue.get()
        if event_data is None:
            # Если очередь пустая
            time.sleep(10)
        else:
            event_id, cur_status = event_data

            print(f"Event with id={event_id} processing...")
            try:
                # Статус - в обработке
                await update_video_status(analisys_id=cur_status, status=1)
                await process_event(event_id)

                # Статус - успешно обработано
                await update_video_status(analisys_id=cur_status, status=2)
            except Exception as e:
                print(f"Error processing event {event_id}: {e}")
                # Статус - ошибка обработки
                await update_video_status(analisys_id=cur_status, status=3)

def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_event_background())

def create_app():
    app = Flask(__name__)

    # Регистрируем blueprint для маршрутов
    app.register_blueprint(video_bp)

    # Запуск фонового потока для обработки очереди
    thread = threading.Thread(target=run_asyncio_loop)
    thread.daemon = True
    thread.start()

    return app