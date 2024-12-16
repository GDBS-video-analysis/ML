import asyncpg
import pytz
from app.config import Config
from datetime import datetime

postgres_uri = Config.POSTGRES_URI

async def insert_video_status(event_id: int, status: int) -> int:
    """
    Вставляет новую запись в таблицу video_analisys_statuses и возвращает analisys_id.
    Использует videofile_id из таблицы events.
    """
    conn = await asyncpg.connect(postgres_uri)
    try:
        get_videofile_id_query = """
        SELECT "videofile_id"
        FROM public."events"
        WHERE "event_id" = $1
        """
        row = await conn.fetchrow(get_videofile_id_query, event_id)
        
        if not row:
            raise ValueError(f"No event found with event_id {event_id}")

        videofile_id = row["videofile_id"]

        insert_query = """
        INSERT INTO public.video_analisys_statuses ("videofile_id", "event_id", "status")
        VALUES ($1, $2, $3)
        RETURNING "analisys_id"
        """
        insert_row = await conn.fetchrow(insert_query, videofile_id, event_id, status)

        return insert_row["analisys_id"]
    finally:
        await conn.close()

async def update_video_status(analisys_id: int, status: int) -> None:
    """
    Обновляет статус записи в таблице video_status по analisys_id.
    """
    conn = await asyncpg.connect(postgres_uri)
    try:
        query = """
        UPDATE public.video_analisys_statuses
        SET "status" = $1
        WHERE "analisys_id" = $2
        """
        await conn.execute(query, status, analisys_id)
    finally:
        await conn.close()

async def insert_employee_marks(event_id: int, data: dict) -> None:
    """
    Вставляет метки времени для сотрудников в таблицу employee_marks_events.
    Добавляет дату мероприятия из таблицы events для каждого videofile_mark.
    """
    conn = await asyncpg.connect(postgres_uri)
    try:
        get_event_date_query = """
        SELECT "date_time"
        FROM public."events"
        WHERE "event_id" = $1
        """
        row = await conn.fetchrow(get_event_date_query, event_id)
        
        if not row:
            raise ValueError(f"No event found with event_id {event_id}")
        
        event_date_utc = row["date_time"].astimezone(pytz.utc)

        insert_query = """
        INSERT INTO public.employee_marks_events (event_id, employee_id, videofile_mark)
        VALUES ($1, $2, $3)
        """
        
        for employee_id, timestamps in data.items():
            employee_id = int(employee_id)
            for timestamp in timestamps:
                
                time_to_add_obj = datetime.strptime(timestamp, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")

                # Добавляем timedelta к объекту datetime
                new_event_date = event_date_utc + time_to_add_obj
                print(f"- Timestamp to save (UTC): {new_event_date}")

                await conn.execute(insert_query, event_id, employee_id, new_event_date)

    except Exception as e:
        print(f"\nError while inserting employees data in database:\n{e}\n")
    finally:
        await conn.close()