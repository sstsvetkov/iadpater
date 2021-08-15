from abc import ABC, abstractmethod

from src.models.db import Database


class Model(ABC):
    @property
    def table_name(self):
        raise NotImplementedError

    @property
    def fields(self):
        raise NotImplementedError

    @property
    def uniques(self):
        raise NotImplementedError

    @property
    def pk(self):
        return NotImplementedError

    def __get_fields(self, fields):
        res = {}
        for field in fields:
            res[field] = self.__getattribute__(field)
        return res

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(name=key, value=value)

    async def save(self):
        try:
            instance = await self.get(**self.__get_fields(self.uniques))
            # await self.__update(instance)
        except self.DoesNotExist:
            await self.__create()
        return self

    async def __create(self):
        db = await Database.get_connection()
        fields = ", ".join(self.fields)
        ids = ", ".join([f"${i}" for i in range(1, len(self.fields) + 1)])
        values = self.__get_fields(self.fields)
        query_string = f"""
            INSERT INTO {self.table_name}({fields})
            VALUES({ids})
            RETURNING *
            """
        res = await db.fetchrow(query_string, *values)
        for key, value in res.items():
            self.__setattr__(name=key, value=value)

    # async def __update(self, old):
    #     db = await Database.get_connection()
    #     await db.execute(
    #         """
    #         UPDATE Phones
    #         SET phone=$1, creation_date=current_timestamp
    #         WHERE row_id=$2
    #         """,
    #         self.phone,
    #         instance.row_id,
    #     )

    @classmethod
    async def update_all(cls, objects):
        pass

    @classmethod
    async def get(cls, **kwargs):
        record = await cls.__get(many=False, **kwargs)
        if record:
            return cls(**record)
        else:
            raise cls.DoesNotExist

    @classmethod
    async def filter(cls, **kwargs):
        records = await cls.__get(many=True, **kwargs)
        return [cls(**record) for record in records]

    @classmethod
    async def __get(cls, many=False, **kwargs):
        query_string = f"SELECT * FROM {cls.table_name}"
        query_string_args = [
            f"{name} = ${ind + 1}" for ind, name in enumerate(kwargs.keys())
        ]
        query_string_args = " AND ".join(query_string_args)
        query_string = query_string + " WHERE " + query_string_args

        db = await Database.get_connection()
        if many:
            return await db.fetchrows(query_string, *kwargs)
        else:
            return await db.fetchrow(query_string, *kwargs)

    class DoesNotExist(Exception):
        pass
