import imaplib
from email.parser import BytesParser
from email.header import decode_header
import re
from time import sleep
from settings import *

import requests

logging.basicConfig(level=logging.INFO)

email_guide = """
ОТКРЫТИЕ ПОЧТЫ НЕ ИЗ СЕТИ ДИКСИ:
Для открытия почты не из сети Дикси можно использовать https://sky.dixy.ru/owa/
Откройте в браузере https://sky.dixy.ru/owa/
Введите свой логин пароль
"""

vpn_guide = """
НАСТРОЙКА VPN:
Выберите необходимую видео инструкцию и следуйте по ней:
https://youtu.be/CZD369T1R1s - Установка OpenVPN на домашнем ПК \ Ноутбуке
https://youtu.be/CiQ-v_MnK0Q - Настройка OpenVPN и подключение к офисному ПК
https://youtu.be/P3RZDWBI-zo - Настройка VPN на iOS
"""


def read_messages(imap):
    imap.select("Inbox")
    response, data = imap.search(None, "UNSEEN")
    uids = data[0].split()
    parser = BytesParser()
    for uid in uids:
        resp, data = imap.fetch(uid, "(RFC822)")
        msg = parser.parsebytes(data[0][1])
        if decode_email_header(msg['Subject']) == "Заведен новый РГМ/ТР":
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        # get the email body
                        body = part.get_payload(decode=True)
                        if body is not None:
                            body = body.decode(encoding="utf-8")
                            data = parse_email(body)
                            if data is None:
                                break
                            telegram_user_id = get_user_id(data["phone"])
                            if telegram_user_id:
                                send_to_user(telegram_user_id, data["msg"])
                                send_to_user(telegram_user_id, email_guide)
                                send_to_user(telegram_user_id, "", "sky.dixy.jpg")
                                send_to_user(telegram_user_id, vpn_guide)
                        # imap.store(uid, '+FLAGS', '(\\Deleted)')
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
            # content_type = msg.get_content_type()
            # body = msg.get_payload(decode=True)
            # if body is not None:
            #     body = body.decode(encoding="windows-1251")
            #     if content_type == "text/html":
            #         data = parse_email(body)
            #         if data is None:
            #             break
            #         telegram_user_id = get_user_id(data["phone"])
            #         if telegram_user_id:
            #             send_to_user(telegram_user_id, data["msg"])
            # imap.store(uid, '+FLAGS', '(\\Deleted)')
    imap.expunge()


def parse_email(body: str):
    try:
        result = re.search("Табельный номер:(.*)ФИО:(.*)Номер телефона:(.*)\\D", body)
        user_id = result.group(1).strip()
        fio = result.group(2).strip()
        phone = parse_phone(result.group(3).strip())
        msg = body.split("---------------------------", 1)[1].replace("Ответственный", "\nОтветственный").replace(
            "Наряд", "\nНаряд").replace("Решение", "\nРешение")
        return {
            "user_id": user_id,
            "phone": phone,
            "fio": fio,
            "msg": msg
        }
    except Exception:
        return None


def decode_email_header(header):
    header_bytes, encoding = decode_header(header)[0]
    if encoding is None:
        return header_bytes
    return header_bytes.decode(encoding)


def send_to_user(user_id, message, image=None):
    if image is None:
        response = requests.get(
            f"https://api.telegram.org/bot1335882907:AAEBfQIQESeXkRCWMsrIwkoUr8NLhK9S7Wc/sendMessage?chat_id={user_id}&text={message}")
    else:
        files = {"photo": open(image, "rb")}
        response = requests.post(
            f"https://api.telegram.org/bot1335882907:AAEBfQIQESeXkRCWMsrIwkoUr8NLhK9S7Wc/sendPhoto?chat_id={user_id}&caption={message}",
            files=files)

    if response.status_code == 200:
        logging.info(
            f" Message send. Userid: {user_id}.\n"
            f"Msg: {message}"
        )
    else:
        logging.error(
            f" Message not send. Status code: {response.status_code}. Userid: {user_id}.\n"
            f"Msg: {message}"
        )
    return response.status_code == 200


def get_user_id(phone) -> int or None:
    params = {"serviceId": "373a98b7-6b91-4701-84e9-2276ea27f254"}
    data = {"and": [{"field": {"static": "ChannelId"}, "in": ["0d33b11c-20af-4781-a992-9e8aef0cc3b5"]},
                    {"field": {"payload": "userPhone"}, "ilike": f"%{phone}%"}]}
    response = requests.post(f"http://{AUTOFAQ_SERVICE_HOST}/api/channelUserResolver", params=params, json=data)
    response_json = response.json()
    if response_json:
        return response_json[0].get("id", None)
    return None


def parse_phone(phone: str) -> int:
    phone = ''.join(re.findall(r'\d+', phone))
    if len(phone) < 10:
        raise ValueError
    try:
        phone = int(phone[len(phone) - 10:])
    except:
        raise ValueError
    return phone


def connect():
    for attempt in range(3):
        try:
            imap = imaplib.IMAP4_SSL(IMAP_HOST, port=IMAP_PORT)
            imap.login(IMAP_USER, IMAP_PASSWD)
            return imap
        except Exception as e:
            if attempt == 2:
                raise e
            sleep(DELAY * 2)


def main():
    while True:
        imap = connect()
        while True:
            try:
                read_messages(imap)
                sleep(DELAY)
            except Exception:
                break


if __name__ == '__main__':
    main()
