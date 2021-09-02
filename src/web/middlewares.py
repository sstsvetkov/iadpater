from aiohttp import web

from settings import SECRET


async def db_handler(app, handler):
    async def middleware(request):
        request.db = app["db"]
        response = await handler(request)
        return response

    return middleware


async def authorize(app, handler):
    async def middleware(request):
        # if request.path.startswith(
        #     ("/api/login", "/api/register", "/api/logout", "/api/ws")
        # ):
        #     response = await handler(request)
        #     return response
        # TODO
        auth = request.headers.get("Authorization", None)
        if auth:
            try:
                token = auth.split(" ")[1]
                if token == SECRET:
                    response = await handler(request)
                    return response
            except Exception:
                pass
        raise web.HTTPUnauthorized

    return middleware
