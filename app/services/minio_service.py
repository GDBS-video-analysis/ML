import os
from minio import Minio
from app.config import Config
from app.services.db_queries import fetch_employee_files, fetch_event_video_path

minio_client = Minio(
    Config.MINIO_FILES_DB_ENDPOINT,
    access_key=Config.MINIO_ACCESS_KEY,
    secret_key=Config.MINIO_SECRET_KEY,
    secure=False
)

async def get_employees_bio() -> dict:
    """
    Получает данные о файлах сотрудников, скачивает их из MinIO 
    и возвращает словарь с путями к папкам для каждого сотрудника.
    """
    rows = await fetch_employee_files()

    os.makedirs(Config.BIOMETRY_DIR, exist_ok=True)
    employee_folders = {}

    for row in rows:
        employee_id, file_id, file_path = row["EmployeesEmployeeID"], row["file_id"], row["path"]
        try:
            employee_dir = os.path.join(Config.BIOMETRY_DIR, str(employee_id))
            if employee_id not in employee_folders:
                os.makedirs(employee_dir, exist_ok=True)
                employee_folders[employee_id] = employee_dir

            local_file_path = os.path.join(employee_dir, os.path.basename(file_path))

            minio_client.fget_object(Config.MINIO_BUCKET, file_path, local_file_path)

        except Exception as e:
            print(f"Failed to download {file_path}.\nError: {e}")
    
    print("Employees biometry successfully downloaded.\n")
    return employee_folders


async def get_event_video(event_id: int) -> str:
    """
    Скачивает видеофайл, привязанный к указанному event_id, из MinIO.
    Возвращает локальный путь к файлу.
    """
    file_path = await fetch_event_video_path(event_id)

    os.makedirs(Config.VIDEO_DIR, exist_ok=True)

    local_file_path = os.path.join(Config.VIDEO_DIR, os.path.basename(file_path))

    try:
        minio_client.fget_object(Config.MINIO_BUCKET, file_path, local_file_path)
        print("Video successfully downloaded.\n")
        return local_file_path
    except Exception as e:
        print(f"Failed to download video for event_id {event_id}.\nError: {e}")
        raise