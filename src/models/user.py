from datetime import datetime
from typing import Optional


class UserQuerySet:
    @staticmethod
    def update(user: 'User'):
        pass


class User:
    query_set = UserQuerySet
    row_id: Optional[int]
    user_id: str
    email: Optional[str]
    full_name: Optional[str]
    position: Optional[str]
    phone: Optional[str]
    extra_phone: Optional[str]
    user_tg_id: Optional[str]
    last_auth: Optional[datetime]

    def __init__(
        self,
        user_id: str,
        email=None,
        full_name=None,
        position=None,
        phone=None,
        extra_phone=None,
        user_tg_id=None,
        last_auth=None,
    ):
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.position = position
        self.phone = phone
        self.extra_phone = extra_phone
        self.user_tg_id = user_tg_id
        self.last_auth = last_auth

    def save(self):
        if self.row_id:
            self.query_set.update(self)
