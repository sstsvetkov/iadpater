from abc import ABC, abstractmethod, abstractstaticmethod
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

    @abstractmethod
    async def get(self):
        pass

    @classmethod
    async def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        return cls(**await cls.query_set.insert(instance))

    async def update(self, merge=True, *args, **kwargs):
        if merge:
            self.query_set.update()



    async def save(self, **kwargs, update=):
        for field, value in self.__dict__.items():
            if isinstance(value, Model):
                await value.save(**kwargs.get(field))
            else:
                self
    #     if not self.row_id:
    #         user_row = await self.get()
    #         if user_row:
    #             self.__class__(**user_row).update(self, recursive=False)
    #
    #     await self.query_set.update(self)
    #
    # def update(self, instance, recursive=True):
    #     for field, value in self.__dict__.items():
    #         if isinstance(value, Model):
    #             if recursive:
    #                 value.update(instance.__getattribute__(field))
    #         else:
    #             self.__setattr__(
    #                 field, instance.__getattribute__(field) or value or None
    #             )
