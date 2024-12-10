# Запуск локалки с моделью

import asyncio
from app import create_app
from app.model_debug import process_video_with_employees
from app.routes import get_event_video, get_employees_bio

# Пример вызова
async def main():
    test_ivent_id = 2
    employees_bio = await get_employees_bio()
    video_path = await get_event_video(test_ivent_id)
    results = process_video_with_employees(video_path=video_path, employee_folders=employees_bio)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
    
# print("Запуск сервера...")
# app = create_app()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
#     print("Сервер запущен.")