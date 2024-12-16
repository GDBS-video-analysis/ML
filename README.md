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

| Файл/Класс                   | Назначение                                           | Методы                                                                                 |
|------------------------------|-----------------------------------------------------|---------------------------------------------------------------------------------------|
| `services/db_queries.py`     | Получение данных из базы данных.                    | - `fetch_employee_files()`: Получает список файлов сотрудников.                        |
|                              |                                                     | - `fetch_event_video_path(event_id)`: Получает путь к видеофайлу мероприятия по `event_id`. |
| `services/db_service.py`     | Операции записи данных в базу данных.               | - `insert_video_status(event_id, status)`: Добавляет запись о статусе анализа видео.   |
|                              |                                                     | - `update_video_status(analisys_id, status)`: Обновляет статус по анализу.             |
|                              |                                                     | - `insert_employee_marks(event_id, data)`: Сохраняет временные метки сотрудников.      |
| `services/minio_service.py`  | Взаимодействие с MinIO для загрузки и сохранения данных. | - `get_employees_bio()`: Получает данные о сотрудниках, загружает из MinIO.           |
|                              |                                                     | - `get_event_video(event_id)`: Загружает видео мероприятия из MinIO.                  |
|                              |                                                     | - `save_unregister_persons_event(data, event_id)`: Сохраняет данные о незнакомых людях. |
| `services/model_service.py`  | Основная обработка видео.                           | - `process_video_final(video_path, employee_folders)`: Обрабатывает видео и сохраняет данные. |
|                              |                                                     | - `[Deprecated] process_video(video_path, employee_folders)`: Устаревший метод обработки видео. |
| `processing.py`              | Класс, содержащий основную логику обработки мероприятия. | - `process_event()`: Обрабатывает мероприятие (биометрия, видео, результаты).          |
| `config.py`                  | Настройка параметров приложения (база данных, MinIO, Flask и локальные директории). | - Конфигурационные параметры для PostgreSQL, MinIO и Flask.                           |
| `routes.py`                  | Определение маршрутов Flask-сервера.               | - `process_event`: Запускает обработку мероприятия.                                    |



