import logging
from typing import TypedDict

import requests

from settings import AUTOFAQ_SERVICE_HOST, DEBUG
from utils import parse_phone


def send_to_user(user_id, message, image=None):
    if DEBUG:
        user_id = 696641812
        logging.debug(f"SEND TO USER - User id: {user_id} Message: {message}")
        return True
    try:
        if image is None:
            response = requests.get(
                f"https://api.telegram.org/bot1335882907:AAEBfQIQESeXkRCWMsrIwkoUr8NLhK9S7Wc/sendMessage?chat_id={user_id}&text={message}"
            )
        else:
            files = {"photo": open(image, "rb")}
            response = requests.post(
                f"https://api.telegram.org/bot1335882907:AAEBfQIQESeXkRCWMsrIwkoUr8NLhK9S7Wc/sendPhoto?chat_id={user_id}&caption={message}",
                files=files,
            )

        if response.status_code == 200:
            logging.info(f"SEND TO USER - User id: {user_id} Message: {message}")
        else:
            logging.error(
                f"SEND TO USER - User id: {user_id} Message: {message} Response: {response}"
            )
        return response.status_code == 200
    except Exception:
        logging.exception(f"SEND TO USER - User id: {user_id} Message: {message}")
        return False


class TgInfo(TypedDict):
    phone: str
    id: str


def get_tg_id(phone=None, user_id=None) -> TgInfo or None:
    if not phone and not user_id:
        return None
    params = {"serviceId": "373a98b7-6b91-4701-84e9-2276ea27f254"}
    q = []
    if phone:
        q.append = {"field": {"payload": "userPhone"}, "ilike": f"%{phone}%"}
    if user_id:
        q.append = {"field": {"payload": "user_num"}, "ilike": f"%{user_id}%"}

    data = {
        "and": [
            {
                "field": {"static": "ChannelId"},
                "in": ["0d33b11c-20af-4781-a992-9e8aef0cc3b5"],
            },
            {"or": q},
        ]
    }
    response = requests.post(
        f"http://{AUTOFAQ_SERVICE_HOST}/api/channelUserResolver",
        params=params,
        json=data,
    )
    response_json = response.json()
    if (
        response_json
        and response_json[0]
        and response_json[0].get_user_by_phone("phone", None)
        and response_json[0].get_user_by_phone("id", None)
    ):
        return response_json[0]["id"], str(parse_phone(response_json[0]["phone"]))
    return None
