import imaplib
import re
import smtplib
from typing import TypedDict
from email.header import decode_header
from email.parser import BytesParser
from time import sleep

import asyncio
import requests

from settings import *
from src.mailadapter import queries
from src.mailadapter.user_info import UserInfo

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


async def read_messages(imap):
    imap.select("Inbox")
    response, data = imap.search(None, "UNSEEN")
    uids = data[0].split()
    parser = BytesParser()
    for uid in uids:
        resp, data = imap.fetch(uid, "(RFC822)")
        msg = parser.parsebytes(data[0][1])
        subject = decode_email_header(msg["Subject"])
        if subject == "Заведен новый РГМ/ТР":
            body = get_email_body(msg)
            try:
                user_info: UserInfo = parse_email_closed(body)
            except ValueError:
                logging.exception("Failed to parse email")
                break
            await handle_order_closed(user_info)

        elif "Зарегистрировано Обр.№" in subject:
            body = get_email_body(msg)
            try:
                user_info: UserInfo = parse_email_created(body)
            except ValueError:
                logging.exception("Failed to parse email")
    imap.expunge()


async def handle_order_closed(user_info: UserInfo):
    try:
        record = await queries.get(user_id=user_info["user_id"])
        if record['send_date'] is not None:
            return
    except Exception:
        pass
    telegram_user_id = get_tg_id(user_info["phone"])
    if telegram_user_id:
        send_to_user(telegram_user_id, user_info["message"])
        send_to_user(telegram_user_id, email_guide)
        send_to_user(telegram_user_id, "", "sky.dixy.jpg")
        send_to_user(telegram_user_id, vpn_guide)


def parse_email_closed(body: str) -> UserInfo or ValueError:
    try:
        result = re.search("Табельный номер:(.*)ФИО:(.*)Номер телефона:(.*)\\D", body)
        user_id = result.group(1).strip()
        fio = result.group(2).strip()
        phone = parse_phone(result.group(3).strip())
        msg = (
            body.split("---------------------------", 1)[1]
            .replace("Ответственный", "\nОтветственный")
            .replace("Наряд", "\nНаряд")
            .replace("Решение", "\nРешение")
        )
        return {"user_id": user_id, "phone": phone, "fio": fio, "msg": msg}
    except Exception as e:
        raise ValueError from e


def parse_email_created(body: str) -> UserInfo or ValueError:
    try:
        pass
    except Exception as e:
        raise ValueError from e


def get_email_body(msg):
    body = None
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
    return body


def decode_email_header(header):
    header_bytes, encoding = decode_header(header)[0]
    if encoding is None:
        return header_bytes
    return header_bytes.decode(encoding)


def send_to_user(user_id, message, image=None):
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


def get_tg_id(phone) -> int or None:
    params = {"serviceId": "373a98b7-6b91-4701-84e9-2276ea27f254"}
    data = {
        "and": [
            {
                "field": {"static": "ChannelId"},
                "in": ["0d33b11c-20af-4781-a992-9e8aef0cc3b5"],
            },
            {"field": {"payload": "userPhone"}, "ilike": f"%{phone}%"},
        ]
    }
    response = requests.post(
        f"http://{AUTOFAQ_SERVICE_HOST}/api/channelUserResolver",
        params=params,
        json=data,
    )
    response_json = response.json()
    if response_json:
        return response_json[0].get("id", None)
    return None


def parse_phone(phone: str) -> int:
    phone = "".join(re.findall(r"\d+", phone))
    if len(phone) < 10:
        raise ValueError
    try:
        phone = int(phone[len(phone) - 10 :])
    except:
        raise ValueError
    return phone


async def connect():
    for attempt in range(3):
        try:
            imap = imaplib.IMAP4_SSL(IMAP_HOST, port=IMAP_PORT)
            imap.login(IMAP_USER, IMAP_PASSWD)
            return imap
        except Exception as e:
            if attempt == 2:
                raise e
            await asyncio.sleep(DELAY * 2)


async def main():
    while True:
        imap = await connect()
        while True:
            try:
                await read_messages(imap)
                await asyncio.sleep(DELAY)
            except Exception:
                break


def send_mail(toaddrs, subject, text):
    fromaddr = SMTP_FROM
    msg = f"Subject: {subject}\n\n{text}"
    server = smtplib.SMTP(IMAP_HOST)
    # server.login(user=IMAP_USER, password=IMAP_PASSWD)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


async def async_main():
    # await new_order(user_id="ДЮ-121212", full_name=None)
    # await queries.msg_send(
    #     user_id="ДЮ-121212", full_name="kek", phone="123", user_tg_id="1245", message="msg"
    #
    r = await queries.get(user_id="ДЮ-121212")
    print(r)


if __name__ == "__main__":
    # asyncio.run(async_main())
    # send_mail()
    pass
