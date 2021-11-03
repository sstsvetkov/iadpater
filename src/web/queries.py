# TABLE Phones
# row_id SERIAL NOT NULL PRIMARY KEY,
# user_id varchar(64) NOT NULL UNIQUE,
# phone   varchar(16) NOT NULL,
# creation_date timestamp not null default current_timestamp

from models import Database
from web.incident import Incident


async def add_phone(user_id: str, phone: str):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        await con.execute(
            """
            INSERT INTO phones(user_id, phone, creation_date)
            VALUES ($1, $2, current_timestamp)
            ON CONFLICT (user_id) DO UPDATE
                SET phone = excluded.phone,
                    creation_date = excluded.creation_date
            """,
            user_id,
            phone,
        )


async def get(phone: str):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(
            """
            SELECT * FROM phones
            WHERE phone=$1
            """,
            phone,
        )


async def update_incident(incident: Incident):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(
            """
            INSERT INTO incidents(incident_uid, user_tg_id, status)
            VALUES ($1, $2, $3)
            ON CONFLICT (incident_uid) DO UPDATE
                SET user_tg_id = excluded.user_tg_id,
                    status = excluded.status
            RETURNING *
            """,
            incident.incident_uid,
            incident.user_tg_id,
            incident.status,
        )


async def get_incident(incident_uid: str):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(
            """
            SELECT * FROM incidents WHERE incident_uid = $1
            """,
            incident_uid,
        )
