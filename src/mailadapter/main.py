import asyncio
import imaplib
from datetime import datetime
from email.parser import BytesParser

from settings import *
from mailadapter import queries
from mailadapter.chat_bot import get_tg_id, send_to_user
from mailadapter.mail import (
    get_email_body,
    decode_email_header,
    parse_email_closed,
    parse_email_created,
    send_mail,
)
from user_info import UserInfo

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
                await handle_order_closed(user_info)
            except ValueError:
                logging.exception("Failed to parse email")

        elif "Зарегистрировано Обр." in subject:
            body = get_email_body(msg)
            try:
                user_info: UserInfo = parse_email_created(body)
                await handle_order_create(user_info)
            except ValueError:
                logging.exception("Failed to parse email")
    imap.expunge()


async def handle_order_closed(user_info: UserInfo):
    record = await queries.get(user_id=user_info["user_id"])
    if record:
        if record["send_date"] is not None:
            # Данные уже были отправлены
            return
        user_info["user_tg_id"] = record["user_tg_id"]

        is_success = send_to_user(user_info["user_tg_id"], user_info["message"])
        send_to_user(user_info["user_tg_id"], email_guide)
        send_to_user(user_info["user_tg_id"], "", "sky.dixy.jpg")
        send_to_user(user_info["user_tg_id"], vpn_guide)
        if is_success:
            user_info["date"] = datetime.now().strftime("%d.%m.%Y")
            send_to_itil(user_info)
            await queries.msg_send(user_info)
    else:
        # Данные ещё не отправлялись
        try:
            tg_info = get_tg_id(user_id=user_info["user_id"])
            if tg_info:
                user_info["user_tg_id"], user_info["phone"] = tg_info
                is_success = send_to_user(user_info["user_tg_id"], user_info["message"])
                send_to_user(user_info["user_tg_id"], email_guide)
                send_to_user(user_info["user_tg_id"], "", "sky.dixy.jpg")
                send_to_user(user_info["user_tg_id"], vpn_guide)
                if is_success:
                    user_info["date"] = datetime.now().strftime("%d.%m.%Y")
                send_to_itil(user_info)
                await queries.msg_send(user_info=user_info)
        except Exception:
            logging.exception("Failed send to itil")


def send_to_itil(user_info: UserInfo):
    subject = (
        "Событие: пользователь авторизовался в чат боте"
        if "data" in user_info
        else "Событие: чат бот отравил сообщение пользователю"
    )
    text = f"#Табельный номер={user_info['user_id']}#\t\n#Номер телефона=7{user_info['phone']}#\t\n#Авторизация пользователя в боте (поделиться номером)={str(bool(user_info['user_tg_id'])).lower()}#\t\n#Отправлено сообщение={str(bool(user_info.get('date', False))).lower()}#\t\n#Дата отправки={user_info.get('date', 'null')}#"

    send_mail(ITIL_EMAIL, subject=subject, text=text)


async def handle_order_create(user_info: UserInfo):
    record = await queries.get(user_id=user_info["user_id"])
    if record:
        if record["user_tg_id"] is not None:
            # Данные уже были отправлены
            return
    else:
        # Данные ещё не отправлялись
        try:
            tg_info = get_tg_id(user_id=user_info["user_id"])
            if tg_info:
                user_info["user_tg_id"], user_info["phone"] = tg_info
                send_to_itil(user_info)
                await queries.new_order(user_info)
        except Exception:
            logging.exception("Failed send to itil")


async def connect():
    for attempt in range(3):
        try:
            imap = imaplib.IMAP4_SSL(IMAP_HOST, port=IMAP_PORT)
            imap.login(IMAP_USER, IMAP_PASSWD)
            logging.info("Connecting to mail server")
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
                logging.exception(msg="Error")
                break


async def async_main():
    # await new_order(user_id="ДЮ-121212", full_name=None)
    # await queries.msg_send(
    #     user_id="ДЮ-121212", full_name="kek", phone="123", user_tg_id="1245", message="msg"
    #
    r = await queries.get(user_id="ДЮ-121212")
    print(r)


if __name__ == "__main__":
    # asyncio.run(async_main())
    asyncio.run(main())
    pass
