import logging

import requests

from mailadapter.settings import AUTOFAQ_SERVICE_HOST, DEBUG


def send_to_user(user_id, message, image=None):
    if DEBUG:
        logging.debug(f" Message send. Userid: {user_id}.\n" f"Msg: {message}")
        return True
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
        logging.info(f" Message send. Userid: {user_id}.\n" f"Msg: {message}")
    else:
        logging.error(
            f" Message not send. Status code: {response.status_code}. Userid: {user_id}.\n"
            f"Msg: {message}"
        )
    return response.status_code == 200


def get_tg_id(phone=None, user_id=None) -> tuple[str, str] or None:
    params = {"serviceId": "373a98b7-6b91-4701-84e9-2276ea27f254"}
    if phone:
        s = {"field": {"payload": "userPhone"}, "ilike": f"%{phone}%"}
    elif user_id:
        s = {"field": {"payload": "user_num"}, "ilike": f"%{user_id}%"}
    else:
        return None
    data = {
        "and": [
            {
                "field": {"static": "ChannelId"},
                "in": ["0d33b11c-20af-4781-a992-9e8aef0cc3b5"],
            },
            s,
        ]
    }
    response = requests.post(
        f"http://{AUTOFAQ_SERVICE_HOST}/api/channelUserResolver",
        params=params,
        json=data,
    )
    response_json = response.json()
    if response_json:
        phone = response_json[0].get("phone", None)
        if phone:
            phone = phone[1:]
        return response_json[0].get("id", None), phone
    return None
