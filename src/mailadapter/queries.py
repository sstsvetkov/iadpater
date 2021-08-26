from mailadapter.user_info import Record
from models.db import Database

"""
row_id SERIAL NOT NULL PRIMARY KEY,
user_id varchar(64),
user_tg_id varchar(64),
message varchar(2048),
phone   varchar(16),
full_name varchar(128),
creation_date timestamp not null default current_timestamp
"""


async def msg_send(record: Record, db=None):
    db = db or await Database.get_connection()
    return await db.fetchrow(
        """
        INSERT INTO records(user_id, user_tg_id, phone, message, full_name, send_date)
        VALUES ($1, $2, $3, $4, $5, current_timestamp)
        ON CONFLICT (user_id) DO UPDATE
            SET user_tg_id = excluded.user_tg_id,
                phone = excluded.phone,
                message = excluded.message,
                full_name = excluded.full_name,
                send_date = excluded.send_date
        RETURNING *
        """,
        record.user_id,
        record.user_tg_id,
        record.phone,
        record.message,
        record.full_name,
    )


async def update(record: Record, db=None):
    db = db or await Database.get_connection()
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
        record.user_id,
        record.user_tg_id,
        record.phone,
        record.message,
        record.full_name,
    )


async def get(user_id, db=None):
    db = db or await Database.get_connection()
    return await db.fetchrow(
        """
        SELECT * FROM records
        WHERE user_id=$1
        """,
        user_id,
    )


async def get_all(db=None):
    db = db or await Database.get_connection()
    return await db.fetch(
        """
        SELECT * FROM records
        """
    )
