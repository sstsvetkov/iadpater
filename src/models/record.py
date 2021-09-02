from datetime import datetime
from enum import Enum
from typing import Optional

from models import Database
from models.model import Model, QuerySet
from models.user import User


class States(Enum):
    NONE = 0
    AUTH = 1
    MSG_SEND = 2


class RecordQuerySet(QuerySet):
    @staticmethod
    async def get(user_id: str):
        db = await Database.get_connection()
        return await db.fetchrow(
            """
            SELECT * FROM records as r
            JOIN users u on u.row_id = r.user_fk
            WHERE u.user_id=$1
            """,
            user_id,
        )

    async def insert(self, *args, **kwargs):
        pass

    @staticmethod
    async def update(record):
        db = await Database.get_connection()
        await db.fetchrow(
            """
            INSERT INTO records(user_fk, message, send_date, itil_send_date)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_fk) DO UPDATE
                SET message = excluded.message or message,
                send_date = excluded.send_date or send_date,
                itil_send_date = excluded.itil_send_date or itil_send_date
            RETURNING *
            """,
            record.user.row_id,
            record.message,
            record.send_date,
            record.itil_send_date,
        )


class Record(Model):
    user: User
    message: Optional[str]
    send_date: Optional[datetime]
    itil_send_date: Optional[datetime]

    def __init__(self, user, send_date=None, message=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.send_date = send_date
        self.message = message

    @staticmethod
    async def get(user_id: str):
        return Record(Record.query_set.get())

    # def update(self, record: "Record"):
    #     self.phone = record.phone or self.phone
    #     self.message = record.message or self.message

    def __str__(self):
        return str(self.__dict__)

    @property
    def state(self) -> States:
        if self.send_date and self.user.user_tg_id:
            return States.MSG_SEND
        elif self.user.user_tg_id:
            return States.AUTH
        return States.NONE
