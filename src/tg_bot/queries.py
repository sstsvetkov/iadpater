from models import Database


async def update_receiver(tg_dialog_id: str, send_notifications: bool):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(
            """
            INSERT INTO receivers(tg_dialog_id, send_notifications)
            VALUES ($1, $2)
            ON CONFLICT (tg_dialog_id) DO UPDATE
                SET send_notifications = excluded.send_notifications
            RETURNING *
            """,
            str(tg_dialog_id),
            send_notifications,
        )


async def get_receiver(tg_dialog_id: str):
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetchrow(
            """
            SELECT * FROM receivers WHERE tg_dialog_id = $1
            """,
            str(tg_dialog_id),
        )


async def get_active_receivers():
    pool = await Database.get_connection_pool()
    async with pool.acquire() as con:
        return await con.fetch(
            """
            SELECT * FROM receivers WHERE send_notifications = TRUE
            """
        )
