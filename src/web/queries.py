# TABLE Phones
# row_id SERIAL NOT NULL PRIMARY KEY,
# user_id varchar(64) NOT NULL UNIQUE,
# phone   varchar(16) NOT NULL,
# creation_date timestamp not null default current_timestamp
from models import Database


async def add_phone(user_id: str, phone: str):
    db = await Database.get_connection()
    await db.execute(
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


async def get_user_by_phone(phone: str):
    db = await Database.get_connection()
    return await db.fetchrow(
        """
        SELECT * FROM phones
        WHERE phone=$1
        """,
        phone,
    )
