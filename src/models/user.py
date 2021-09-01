from datetime import datetime
from typing import Optional

from models import Database
from models.model import Model, QuerySet


class UserQuerySet(QuerySet):
    @staticmethod
    async def get(user_id: str):
        db = await Database.get_connection()
        return await db.fetchrow(
            """
            SELECT * FROM users
            WHERE user_id=$1
            """,
            user_id,
        )

    @staticmethod
    async def create(user):
        db = await Database.get_connection()
        await db.execute(
            """
            INSERT INTO users(user_id, email, full_name, position, phone, extra_phone, user_tg_id, last_auth)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            user.user_id,
            user.email,
            user.full_name,
            user.position,
            user.phone,
            user.extra_phone,
            user.user_tg_id,
            user.last_auth,
        )

    @staticmethod
    async def update(user):
        db = await Database.get_connection()
        await db.execute(
            """
            INSERT INTO users(user_id, email, full_name, position, phone, extra_phone, user_tg_id, last_auth)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (user_id) DO UPDATE
                SET email = excluded.email or email,
                full_name = excluded.full_name or full_name,
                position = excluded.position or position,
                phone = excluded.phone or phone,
                extra_phone = excluded.extra_phone or extra_phone,
                user_tg_id = excluded.user_tg_id or user_tg_id,
                last_auth = excluded.last_auth or last_auth
            """,
            user.user_id,
            user.email,
            user.full_name,
            user.position,
            user.phone,
            user.extra_phone,
            user.user_tg_id,
            user.last_auth,
        )


class User(Model):
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
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.email = email
        self.full_name = full_name
        self.position = position
        self.phone = phone
        self.extra_phone = extra_phone
        self.user_tg_id = user_tg_id
        self.last_auth = last_auth

    async def get(self):
        return self.query_set.get(user_id=self.user_id)
