from datetime import datetime
import io
import os
import uuid
import asyncpg
from minio import Minio
import pytz
from app.config import Config
from app.services.db_queries import fetch_employee_files, fetch_event_video_path

minio_client = Minio(
    Config.MINIO_ENDPOINT,
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


async def save_unregister_persons_event(data, event_id):
    """
    Сохраняет данные о неопознанных лицах, их временных метках и файлах в MinIO и БД.
    """
    conn = await asyncpg.connect(Config.POSTGRES_URI)

    try:
        # Получаем дату события для привязки временных меток
        get_event_date_query = """
        SELECT "date_time"
        FROM public."events"
        WHERE "event_id" = $1
        """
        row = await conn.fetchrow(get_event_date_query, event_id)
        
        if not row:
            raise ValueError(f"No event found with event_id {event_id}")
        
        event_date_utc = row["date_time"].astimezone(pytz.utc)
        event_date = event_date_utc.strftime('%Y-%m-%d') 

        for person_id, details in data.items():
            image_path = details["path"]
            timestamps = details["timestamps"]
            image_path = os.path.join(image_path, "face.jpg")

            if not os.path.exists(image_path):
                print(f"- No file at path: {image_path}\n")
                continue

            if not os.access(image_path, os.R_OK):
                print(f"- No access to file: {image_path}\n")
                continue

            with open(image_path, "rb") as image_file:
                file_data = image_file.read()

            unique_key = f"{uuid.uuid4()}-unknown_face{person_id}"
            minio_path = f"unregister_faces/{unique_key}/{os.path.basename(image_path)}"

            minio_client.put_object(
                Config.MINIO_BUCKET, minio_path, io.BytesIO(file_data), length=len(file_data), content_type="image/png"
            )

            file_query = """
            INSERT INTO files (path, name, size, mimetype, created_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING file_id
            """
            file_name = os.path.basename(image_path)
            file_size = len(file_data)
            file_created_at = datetime.now(pytz.utc)

            file_id = await conn.fetchval(
                file_query, minio_path, file_name, file_size, "image/png", file_created_at
            )

            first_timestamp = timestamps[0]
            time_parts = list(map(int, first_timestamp.split(':')))
            local_time_str = f"{event_date} {time_parts[0]:02}:{time_parts[1]:02}:{time_parts[2]:02}"

            # Создаем datetime объект с временной меткой
            utc_datetime = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)

            print(f"First Timestamp to save (UTC): {utc_datetime}")

            mark_query = """
            INSERT INTO public.unregister_person_marks_events (event_id, videofile_fragment_id, videofile_mark)
            VALUES ($1, $2, $3)
            RETURNING unregister_person_id
            """

            unregister_person_id = await conn.fetchval(
                mark_query, event_id, file_id, utc_datetime
            )

            timestamps_query = """
            INSERT INTO public.unregister_person_marks_events (
                event_id, videofile_fragment_id, unregister_person_id, videofile_mark
            ) VALUES ($1, $2, $3, $4)
            """

            for timestamp in timestamps[1:]:
                # Преобразуем строку временной метки в объект datetime
                time_parts = list(map(int, timestamp.split(':')))
                local_time_str = f"{event_date} {time_parts[0]:02}:{time_parts[1]:02}:{time_parts[2]:02}"

                utc_datetime = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)

                print(f"Timestamp to save (UTC): {utc_datetime}")

                await conn.execute(
                    timestamps_query, event_id, file_id, unregister_person_id, utc_datetime
                )

        print("- - All data about uknown guests saved in DB and MinIO correctly.\n")
    except Exception as e:
        print(f"Error during saving unknown guests.\nError: {e}\n")
    finally:
        await conn.close()