import asyncio
import os

import asyncpg

from mail_adapter import send_to_itil
from mailadapter.user_info import Record
from mailadapter.queries import get_all


async def main():
    db = await asyncpg.connect(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        host="srv-autofaq-dca",
        port=4445,
    )

    users = await get_all(db=db)

    for user in users:
        # u = Record(**user)
        # print(u)
        # if (
        # ):
        #     send_to_user(user["user_id"], user["message"])
        #     send_to_user(user["user_id"], email_guide)
        #     send_to_user(user["user_id"], "", SKY_DIXY_PATH)
        #     send_to_user(user["user_id"], vpn_guide)
        #     await msg_send(user_info=user)
        r = Record(**user)
        if r.user_id == "ДЮ-276238" or r.user_id == "ДЮ-098850":
            send_to_itil(r)

    # print(user)
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
