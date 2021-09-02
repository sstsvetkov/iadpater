from abc import ABC, abstractmethod
from typing import Optional


class QuerySet(ABC):
    @abstractmethod
    async def get(self, *args, **kwargs):
        pass

    @abstractmethod
    async def insert(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update(self, *args, **kwargs):
        pass


class Model(ABC):
    row_id: Optional[str]
    query_set: QuerySet

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        return cls(**await cls.query_set.insert(instance))

    async def save(self):
        for field, value in self.__dict__.items():
            if isinstance(value, Model):
                await value.save()
        row = await self.query_set.update(self)
        self.row_id = row["row_id"]
