from typing import List
import asyncpg
from app.config import Config

async def fetch_employee_files() -> List[dict]:
    """
    Получает список файлов сотрудников из базы данных.
    """
    conn = await asyncpg.connect(Config.POSTGRES_URI)
    try:
        query = """
        SELECT em."EmployeesEmployeeID", f."file_id", f."path"
        FROM public."EmployeeMinioFile" em
        INNER JOIN public."files" f ON em."BiometricsFileID" = f."file_id"
        ORDER BY em."EmployeesEmployeeID" ASC, f."file_id" ASC
        """
        return await conn.fetch(query)
    finally:
        await conn.close()


async def fetch_event_video_path(event_id: int) -> str:
    """
    Получает путь к видеофайлу для указанного event_id из базы данных.
    """
    conn = await asyncpg.connect(Config.POSTGRES_URI)
    try:
        query = """
        SELECT f."path"
        FROM public."events" e
        INNER JOIN public."files" f ON e."videofile_id" = f."file_id"
        WHERE e."event_id" = $1
        """
        row = await conn.fetchrow(query, event_id)
        if row is None:
            raise ValueError(f"No video file found for event_id {event_id}")
        return row["path"]
    finally:
        await conn.close()