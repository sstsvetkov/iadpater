from src.models.db import Database
from src.models.model import Model


class Phone(Model):
    def __init__(self, user_id, phone, row_id: int = None, creation_date=None, **kwargs):
        super().__init__(**kwargs)
        self.row_id = row_id
        self.user_id = user_id
        self.phone = phone
        self.creation_date = creation_date

    @classmethod
    async def create(cls, user_id, phone):
        phone = cls(user_id, phone)
        await phone.save()
        return phone

    async def save(self):
        db = await Database.get_connection()
        phone = await self.get(user_id=self.user_id)
        if phone:
            await db.execute(
                """
                UPDATE Phones
                SET phone=$1, creation_date=current_timestamp
                WHERE row_id=$2
                """,
                self.phone,
                phone.row_id,
            )
        else:
            self.row_id, self.creation_date = await db.fetchrow(
                """
                INSERT INTO Phones(user_id, phone)
                VALUES($1, $2)
                RETURNING row_id, creation_date
                """,
                self.user_id,
                self.phone,
            )
        return self
