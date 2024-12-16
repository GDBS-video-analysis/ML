import os

class Config:
    # PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE", "postgres")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pass")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_URI = (
        f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
    )

    # MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_FILES_DB_ENDPOINT = os.getenv("MINIO_FILES_DB_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "1234")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "12345678")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "dev")
    
    # Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5050))

    # Локальные директории
    LOCAL_DIR = "./processing_data"
    BIOMETRY_DIR = LOCAL_DIR + "/db"
    VIDEO_DIR = LOCAL_DIR
    STRANGERS_DIR = LOCAL_DIR + "/db_unknown"