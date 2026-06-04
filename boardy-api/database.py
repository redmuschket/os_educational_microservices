from contextlib import asynccontextmanager
import aiomysql
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "boardy"),
    "password": os.getenv("DB_PASSWORD", "boardy_password"),
    "db": os.getenv("DB_NAME", "boardy_api"),
    "autocommit": True,
}

@asynccontextmanager
async def get_db():
    connection = await aiomysql.connect(**DB_CONFIG)
    try:
        async with connection.cursor(aiomysql.DictCursor) as cursor:
            yield cursor
    finally:
        connection.close()
