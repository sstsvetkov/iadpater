import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from mailadapter.main import main as mail_adapter
from chat_bot.main import main as chat_bot

from aiohttp import web

from models.db import Database
from web.middlewares import authorize, db_handler
from web.routes import routes


async def init_app():
    app = web.Application(middlewares=[authorize, db_handler])
    db = await Database.get_connection()
    app["db"] = db
    app.add_routes(routes=routes)
    loop = asyncio.get_event_loop()
    thread_pool = ThreadPoolExecutor(2)
    app["mail_adapter_thread"] = loop.run_in_executor(thread_pool, mail_adapter)
    app["bot_thread"] = loop.run_in_executor(thread_pool, chat_bot)
    return app


def main():
    web.run_app(init_app(), host="0.0.0.0", port=4444)


if __name__ == "__main__":
    main()
