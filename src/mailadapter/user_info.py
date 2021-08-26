from datetime import datetime
from enum import Enum
from typing import Optional

from mailadapter.chat_bot import get_tg_id


class States(Enum):
    NONE = 0
    AUTH = 1
    MSG_SEND = 2


class Record:
    user_id: str
    user_tg_id: Optional[str]
    phone: Optional[str]
    full_name: str
    send_date: Optional[datetime]
    message: Optional[str]

    def __init__(
        self,
        user_id,
        full_name,
        user_tg_id=None,
        phone=None,
        send_date=None,
        message=None,
        *args,
        **kwargs
    ):
        self.user_id = user_id
        self.full_name = full_name
        self.user_tg_id = user_tg_id
        self.phone = phone
        self.send_date = send_date
        self.message = message

    def update(self, record: "Record"):
        self.phone = record.phone or self.phone
        self.message = record.message or self.message

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
