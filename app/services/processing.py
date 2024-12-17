import json
from pathlib import Path
import shutil
from app.services import minio_service, model_service, db_service


async def process_event(event_id):
        """
        Основной метод для обработки события:
        1. Получаем данные о сотрудниках.
        2. Получаем видео для указанного события.
        3. Обрабатываем видео с помощью модели.
        
        Возвращает результат обработки.
        """
        event = event_id
        # Получаем биометрические данные сотрудников
        employees_bio = await minio_service.get_employees_bio()

        # Получаем путь к видеофайлу для указанного event_id
        video_path = await minio_service.get_event_video(event)

        # Обрабатываем видео с помощью модели
        results = model_service.process_video_final(video_path=video_path, employee_folders=employees_bio)

        # Вставка информации о сотрудниках в БД
        print("Saving employees data...\n")
        with open('processing_data/employees.json', 'r') as file:
           employees_data = json.load(file)

        await db_service.insert_employee_marks(event_id=event, data=employees_data)

        # Вставка информации о незнакомцах в БД
        print("Saving unknown faces data...\n")
        with open('processing_data/unknown_faces.json', 'r') as file:
            unknown_faces_data = json.load(file)
        await minio_service.save_unregister_persons_event(data=unknown_faces_data, event_id=event)
        
        folder_path = Path('processing_data')
        for file_path in folder_path.iterdir():
            try:
                if file_path.is_file():
                    file_path.unlink()  # Удаляем файл
                elif file_path.is_dir():
                    shutil.rmtree(file_path)  # Рекурсивно удаляем папку и все её содержимое
            except Exception as e:
                print(f"Error during deleting processing data.\nPath: {file_path}\nError: {e}\n")