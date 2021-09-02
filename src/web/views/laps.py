import json

from aiohttp import web
from ldap3 import Server, ALL, Connection, NTLM


def laps(server, user, password, computer_name):
    server = Server(server, get_info=ALL)
    conn = Connection(server=server, user=user, password=password, authentication=NTLM)
    conn.bind()
    conn.search(
        "dc=Dixy,dc=local",
        f"(&(objectclass=computer)(name={computer_name}))",
        attributes=["ms-Mcs-AdmPwd"],
    )
    if conn.entries:
        return str(conn.entries[0]["ms-Mcs-AdmPwd"])
    else:
        return None


class LapsView(web.View):
    async def post(self):
        text = await self.request.text()
        try:
            body = json.loads(text or "{}")
        except json.JSONDecodeError:
            return web.Response(status=400)
        server = body.get_user_by_phone("server", None)
        user = body.get_user_by_phone("user", None)
        password = body.get_user_by_phone("password", None)
        computer_name = body.get_user_by_phone("computerName", None)
        if server and user and password and computer_name is not None:
            text = (
                laps(
                    server=server,
                    user=user,
                    password=password,
                    computer_name=computer_name,
                )
                or "0"
            )
        else:
            text = "0"
        return web.Response(text=text)
