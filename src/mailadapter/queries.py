from asyncpg import UniqueViolationError

from src.mailadapter.user_info import UserInfo
from src.models.db import Database

from settings import logging

"""
row_id SERIAL NOT NULL PRIMARY KEY,
user_id varchar(64),
user_tg_id varchar(64),
message varchar(2048),
phone   varchar(16),
full_name varchar(128),
creation_date timestamp not null default current_timestamp
"""


async def new_order(user_info: UserInfo):
    try:
        db = await Database.get_connection()
        await db.execute(
            """
            INSERT INTO records(user_id, full_name, phone, user_tg_id)
            VALUES ($1, $2, $3, $4)
            """,
            user_info["user_id"],
            user_info["full_name"],
            user_info["phone"],
            user_info["user_tg_id"],
        )
    except UniqueViolationError as e:
        logging.error(e)


async def greetings(user_id, user_tg_id):
    db = await Database.get_connection()
    await db.execute(
        """
        UPDATE records
        SET user_tg_id=$1
        WHERE user_id=$2
        """,
        user_tg_id,
        user_id,
    )


async def msg_send(user_info: UserInfo):
    db = await Database.get_connection()
    await db.execute(
        """
        INSERT INTO records(user_id, user_tg_id, phone, message, full_name, send_date)
        VALUES ($1, $2, $3, $4, $5, current_timestamp)
        ON CONFLICT (user_id) DO UPDATE
            SET user_tg_id = excluded.user_tg_id,
                phone = excluded.phone,
                message = excluded.message,
                full_name = excluded.full_name,
                send_date = excluded.send_date
        """,
        user_info["user_id"],
        user_info["user_tg_id"],
        user_info["phone"],
        user_info["message"],
        user_info["full_name"],
    )


async def msg_send_failed(user_id, user_tg_id, phone, message, full_name):
    db = await Database.get_connection()
    await db.execute(
        """
        INSERT INTO records(user_id, user_tg_id, phone, message, full_name)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id) DO UPDATE
            SET user_tg_id = excluded.user_tg_id,
                phone = excluded.phone,
                message = excluded.message,
                full_name = excluded.full_name
        """,
        user_id,
        user_tg_id,
        phone,
        message,
        full_name,
    )


async def get(user_id):
    db = await Database.get_connection()
    return await db.fetchrow(
        """
        SELECT * FROM records
        WHERE user_id=$1
        """,
        user_id,
    )