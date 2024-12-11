import asyncpg
from app.config import Config

postgres_uri = Config.POSTGRES_URI

async def insert_video_status(videofile_id: int, event_id: int, status: int) -> int:
    """
    Вставляет новую запись в таблицу video_status и возвращает analisys_id.
    """
    conn = await asyncpg.connect(postgres_uri)
    try:
        query = """
        INSERT INTO public.video_analisys_statuses ("videofile_id", "event_id", "status")
        VALUES ($1, $2, $3)
        RETURNING "analisys_id"
        """
        row = await conn.fetchrow(query, videofile_id, event_id, status)
        return row['analisys_id']
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