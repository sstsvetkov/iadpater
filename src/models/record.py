from datetime import datetime
from enum import Enum
from typing import Optional

from mailadapter.chat_bot import get_tg_id
from models.model import Model, QuerySet
from models.user import User


class States(Enum):
    NONE = 0
    AUTH = 1
    MSG_SEND = 2


class RecordQuerySet(QuerySet):
    async def get(self, *args, **kwargs):
        pass

    async def insert(self, *args, **kwargs):
        pass

    async def update(self, *args, **kwargs):
        pass


class Record(Model):
    user: User
    send_date: Optional[datetime]
    message: Optional[str]

    def __init__(self, user, send_date=None, message=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.send_date = send_date
        self.message = message

    async def get(self):
        pass

    # def update(self, record: "Record"):
    #     self.phone = record.phone or self.phone
    #     self.message = record.message or self.message

    def update_tg_id(self):
        tg_info = get_tg_id(user_id=self.user_id, phone=self.phone)
        if tg_info:
            self.user_tg_id = self.user_tg_id or tg_info[0]
            self.phone = self.phone or tg_info[1]

    def __str__(self):
        return str(self.__dict__)

    @property
    def state(self) -> States:
        if self.send_date and self.user_tg_id:
            return States.MSG_SEND
        elif self.user_tg_id:
            return States.AUTH
        return States.NONE
