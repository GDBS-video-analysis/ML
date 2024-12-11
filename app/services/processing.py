from app.services import minio_service, model_service

class Processing:
    def __init__(self, event_id: int):
        self.event_id = event_id

    async def process_event(self):
        """
        Основной метод для обработки события:
        1. Получаем данные о сотрудниках.
        2. Получаем видео для указанного события.
        3. Обрабатываем видео с помощью модели.
        
        Возвращает результат обработки.
        """
        # Получаем биометрические данные сотрудников
        employees_bio = await minio_service.get_employees_bio()

        # Получаем путь к видеофайлу для указанного event_id
        video_path = await minio_service.get_event_video(self.event_id)

        # Обрабатываем видео с помощью модели
        results = model_service.process_video(video_path=video_path, employee_folders=employees_bio)

        return results