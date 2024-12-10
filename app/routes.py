# Запросы POST и GET

import asyncpg
from flask import Blueprint, request, jsonify
import os
from minio import Minio, S3Error
video_bp = Blueprint('video', __name__)

# Конфигурация PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_URI = (
    f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

# Конфигурация MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
# Я не могу здесь избавиться от localhost:9000!!!! 
MINIO_FILES_DB_ENDPOINT = os.getenv("MINIO_FILES_DB_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "1234")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "12345678")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "dev")

minio_client = Minio(
    MINIO_FILES_DB_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

LOCAL_DIR = "./processing_data"
BIOMETRY_DIR = LOCAL_DIR + "/db"
VIDEO_DIR = LOCAL_DIR

async def get_employees_bio() -> dict:
    """
    Получает данные о файлах сотрудников из БД, скачивает их из MinIO 
    и возвращает словарь с путями к папкам для каждого сотрудника.
    
    Возвращает словарь вида {employee_id: employee_folder_path}.
    """
    conn = await asyncpg.connect(POSTGRES_URI)
    try:
        # Запрос для получения данных
        query = """
        SELECT em."EmployeesEmployeeID", f."file_id", f."path"
        FROM public."EmployeeMinioFile" em
        INNER JOIN public."files" f ON em."BiometricsFileID" = f."file_id"
        ORDER BY em."EmployeesEmployeeID" ASC, f."file_id" ASC
        """
        rows = await conn.fetch(query)
        
        os.makedirs(BIOMETRY_DIR, exist_ok=True)

        employee_folders = {}

        for row in rows:
            employee_id, file_id, file_path = row["EmployeesEmployeeID"], row["file_id"], row["path"]
            try:
                # Создаем папку для сотрудника, если ее нет
                employee_dir = os.path.join(BIOMETRY_DIR, str(employee_id))
                if employee_id not in employee_folders:
                    os.makedirs(employee_dir, exist_ok=True)
                    employee_folders[employee_id] = employee_dir

                # Локальный путь для сохранения файла
                local_file_path = os.path.join(employee_dir, os.path.basename(file_path))

                # Скачивание файла из MinIO
                minio_client.fget_object(MINIO_BUCKET, file_path, local_file_path)

            except Exception as e:
                print(f"Failed to download {file_path}.\nError: {e}")
        
        print("Employees biometry successfully downloaded.\n")
        return employee_folders
    finally:
        await conn.close()


async def get_event_video(event_id: int) -> str:
    """
    Скачивает видеофайл, привязанный к указанному event_id, из MinIO.
    Возвращает локальный путь к файлу.
    """
    conn = await asyncpg.connect(POSTGRES_URI)
    try:
        # Получение пути к видеофайлу для указанного event_id
        query = """
        SELECT f."path"
        FROM public."events" e
        INNER JOIN public."files" f ON e."videofile_id" = f."file_id"
        WHERE e."event_id" = $1
        """
        row = await conn.fetchrow(query, event_id)

        if row is None:
            raise ValueError(f"No video file found for event_id {event_id}")

        file_path = row["path"]

        # Убедиться, что локальная директория для видео существует
        os.makedirs(VIDEO_DIR, exist_ok=True)

        # Локальный путь для сохранения файла
        local_file_path = os.path.join(VIDEO_DIR, os.path.basename(file_path))

        # Скачивание видео из MinIO
        minio_client.fget_object(MINIO_BUCKET, file_path, local_file_path)
        print("Video successfully downloaded.\n")
        return local_file_path
    except Exception as e:
        print(f"Failed to download video for event_id {event_id}.\nError: {e}")
        raise
    finally:
        await conn.close()

@video_bp.route('/process_video', methods=['POST'])
def process_video():
    try:
        video_path = "tests/test_data/video.mp4"
        biometry_path = request.json.get("biometry_path")

        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Video file not found"}), 400

        if not os.path.exists(biometry_path):
            return jsonify({"error": f"Passed path {biometry_path} does not exist!"}), 400

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500