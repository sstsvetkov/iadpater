import requests
from aiohttp import web

from settings import ITIL_API_URL, ITIL_PASS, ITIL_LOGIN


class Incidents(web.View):
    async def get(self):
        user_initiator = self.request.query.get("userInitiator")
        if user_initiator:
            response = requests.get(
                f"{ITIL_API_URL}getListIncidents/?UserInitiator={user_initiator}",
                auth=(ITIL_LOGIN, ITIL_PASS),
            )
            return web.Response(text=response.text, charset="utf-8")
        else:
            return web.Response(status=400)


class Services(web.View):
    async def get(self):
        user_initiator = self.request.query.get("userInitiator")
        if user_initiator:
            response = requests.get(
                f"{ITIL_API_URL}getListServices/?UserInitiator={user_initiator}",
                auth=(ITIL_LOGIN, ITIL_PASS),
            )
            return web.Response(text=response.text, charset="utf-8")
        else:
            return web.Response(status=400)
