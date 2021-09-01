import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from mailadapter.main import main as mail_adapter
from chat_bot.main import main as chat_bot

from aiohttp import web

from models.db import Database


async def init_app():
    app = web.Application()
    db = await Database.get_connection()
    app["db"] = db
    app.add_routes([web.post("/laps", handle_laps)])
    app.add_routes([web.post("/bio", handle_bio)])
    app.add_routes([web.post("/basic-auth", handle_basic_auth)])
    app.add_routes([web.post("/auth", handle_auth_post)])
    app.add_routes([web.get("/auth", handle_auth_get)])
    app.add_routes([web.get("/itil-get-incidents", handle_get_incidents)])
    app.add_routes([web.get("/itil-get-services", handle_get_services)])
    app.add_routes([web.get("/user", handle_get_user)])
    app.add_routes([web.post("/add-user-phone", handle_add_user_phone)])

    loop = asyncio.get_event_loop()
    thread_pool = ThreadPoolExecutor(2)
    app["mail_adapter_thread"] = loop.run_in_executor(thread_pool, mail_adapter)
    app["bot_thread"] = loop.run_in_executor(thread_pool, chat_bot)
    return app


def main():
    web.run_app(init_app(), host="0.0.0.0", port=4444)


if __name__ == "__main__":
    main()
