import os

import asyncpg


class Database(object):
    _instance = None

    @staticmethod
    async def _create_connection():
        return await asyncpg.connect(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            database=os.environ["POSTGRES_DB"],
            host=os.environ["POSTGRES_DB_HOST"],
            port=5432,
        )

    @classmethod
    async def get_connection(cls, new=False):
        if new or not cls._instance:
            cls._instance = await Database._create_connection()
        return cls._instance

    def __exit__(self):
        self._instance.close()
