import os
from minio import Minio
import asyncpg
from app.config import Config

minio_client = Minio(
    Config.MINIO_FILES_DB_ENDPOINT,
    access_key=Config.MINIO_ACCESS_KEY,
    secret_key=Config.MINIO_SECRET_KEY,
    secure=False
)

async def get_employees_bio() -> dict:
    """
    Получает данные о файлах сотрудников из БД, скачивает их из MinIO 
    и возвращает словарь с путями к папкам для каждого сотрудника.
    
    Возвращает словарь вида {employee_id: employee_folder_path}.
    """
    conn = await asyncpg.connect(Config.POSTGRES_URI)
    try:
        # Запрос для получения данных
        query = """
        SELECT em."EmployeesEmployeeID", f."file_id", f."path"
        FROM public."EmployeeMinioFile" em
        INNER JOIN public."files" f ON em."BiometricsFileID" = f."file_id"
        ORDER BY em."EmployeesEmployeeID" ASC, f."file_id" ASC
        """
        rows = await conn.fetch(query)
        
        os.makedirs(Config.BIOMETRY_DIR, exist_ok=True)

        employee_folders = {}

        for row in rows:
            employee_id, file_id, file_path = row["EmployeesEmployeeID"], row["file_id"], row["path"]
            try:
                # Создаем папку для сотрудника, если ее нет
                employee_dir = os.path.join(Config.BIOMETRY_DIR, str(employee_id))
                if employee_id not in employee_folders:
                    os.makedirs(employee_dir, exist_ok=True)
                    employee_folders[employee_id] = employee_dir

                # Локальный путь для сохранения файла
                local_file_path = os.path.join(employee_dir, os.path.basename(file_path))

                # Скачивание файла из MinIO
                minio_client.fget_object(Config.MINIO_BUCKET, file_path, local_file_path)

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
    conn = await asyncpg.connect(Config.POSTGRES_URI)
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
        os.makedirs(Config.VIDEO_DIR, exist_ok=True)

        # Локальный путь для сохранения файла
        local_file_path = os.path.join(Config.VIDEO_DIR, os.path.basename(file_path))

        # Скачивание видео из MinIO
        minio_client.fget_object(Config.MINIO_BUCKET, file_path, local_file_path)
        print("Video successfully downloaded.\n")
        return local_file_path
    except Exception as e:
        print(f"Failed to download video for event_id {event_id}.\nError: {e}")
        raise
    finally:
        await conn.close()