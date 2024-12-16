## Как запустить

1. Убедитесь, что у вас установлены следующие зависимости:
   - Python 3.8.6
   - Flask
   - MinIO
   - PostgreSQL
   - Все зависимости из `requirements.txt`

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt

3. Запустите сервер:
  `python run.py`

4. Обратитесь к `/process_event`, передав в качестве аргументов `event_id` и `videofile_id`.

## Структура проекта

app/ ├── services/ │ ├── db_queries.py │ │ ├── async def fetch_employee_files() -> List[dict]: │ │ │ Получает список файлов сотрудников из базы данных. │ │ ├── async def fetch_event_video_path(event_id: int) -> str: │ │ Получает путь к видеофайлу для указанного event_id из базы данных. │ ├── db_service.py │ │ ├── async def insert_video_status(event_id: int, status: int) -> int: │ │ │ Вставляет новую запись в таблицу video_analisys_statuses и возвращает analisys_id. │ │ ├── async def update_video_status(analisys_id: int, status: int) -> None: │ │ │ Обновляет статус записи в таблице video_status по analisys_id. │ │ ├── async def insert_employee_marks(event_id: int, data: dict) -> None: │ │ Вставляет временные метки для сотрудников в таблицу employee_marks_events. │ ├── minio_service.py │ │ ├── async def get_employees_bio() -> dict: │ │ │ Получает данные о файлах сотрудников из MinIO и возвращает словарь с путями. │ │ ├── async def get_event_video(event_id: int) -> str: │ │ │ Скачивает видеофайл мероприятия по event_id из MinIO. │ │ ├── async def save_unregister_persons_event(data, event_id): │ │ Сохраняет информацию о незнакомых людях для указанного мероприятия. │ ├── model_service.py │ │ ├── def process_video_final(video_path, employee_folders): │ │ │ Обрабатывает видео, сопоставляя лица с папками сотрудников и сохраняет результаты. │ │ ├── [Deprecated] def process_video(video_path, employee_folders): │ │ Устаревший метод обработки видео. │ ├── processing.py │ ├── class Processing: │ │ ├── def init(self, event_id: int): │ │ │ Инициализирует объект для обработки мероприятия. │ │ ├── async def process_event(): │ │ Основной метод обработки мероприятия (биометрия, видео, результаты). ├── config.py │ ├── class Config: │ Конфигурация приложения: │ - Настройки PostgreSQL. │ - Параметры MinIO. │ - Настройки Flask. │ - Локальные директории для обработки данных. ├── routes.py │ ├── @video_bp.route('/process_event', methods=['POST']) │ Асинхронный маршрут для обработки мероприятия. ├── processing_data/ ├── Папка для временных файлов: - Видео мероприятий. - Биометрия сотрудников. - Результаты обработки.



