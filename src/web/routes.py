from aiohttp.web import get, post
from views import *

routes = [
    post("/laps", LapsView, name="laps"),
    # post("/bio", Bio, name="bio"),
    post("/basic-auth", BasicAuthEncode, name="basicAuth"),
    post("/auth", AuthView, name="auth"),
    get("/auth", AuthView, name="auth"),
    get("/itil-get-incidents", Incidents, name="incidents"),
    get("/itil-get-services", Services, name="services"),
    get("/user", UserView, name="user"),
    post("/add-user-phone", AddPhoneView, name="addPhone"),
]
