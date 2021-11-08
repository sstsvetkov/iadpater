import logging
import os

import asyncpg


class Database(object):
    _instance = None

    @staticmethod
    async def _create_pool():
        return await asyncpg.create_pool(
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            database=os.environ["POSTGRES_DB"],
            host=os.environ["POSTGRES_DB_HOST"],
            port=os.environ["POSTGRES_DB_PORT"],
        )

    @classmethod
    async def get_connection_pool(cls, new=False):
        if new or not cls._instance:
            cls._instance = await Database._create_pool()
            logging.info("Created connection pool")
        return cls._instance

    def __exit__(self):
        self._instance.close()
