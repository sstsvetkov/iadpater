import asyncio
import imaplib
import logging
from datetime import timedelta
from email.parser import BytesParser

from mailadapter import *
from mailadapter.chat_bot import send_to_user
from mailadapter.mail import (
    decode_email_header,
    get_email_body,
    parse_email_closed,
    parse_email_created,
    OrderClosedData,
    OrderCreatedData,
)
from models import Database
from models.record import Record, States
from settings import BASE_DIR, DELAY, IMAP_HOST, IMAP_PASSWD, IMAP_USER, IMAP_PORT

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

SKY_DIXY_PATH = BASE_DIR / "src/mailadapter/sky.dixy.jpg"


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
                order_data: OrderClosedData = parse_email_closed(body)
                await handle_order_closed(order_data)
            except ValueError:
                pass

        elif "Зарегистрировано Обр." in subject:
            body = get_email_body(msg)
            try:
                order_data: OrderCreatedData = parse_email_created(body)
                await handle_order_create(order_data)
            except ValueError:
                pass
    imap.expunge()


async def handle_order_closed(data: OrderClosedData):
    record: Record = await Record.query_set.get(user_id=data["user_id"])
    if record:
        if data["phone"]:
            record.user.phone = data["phone"]
        record.user.full_name = data["full_name"]
        record.message = data["message"]

    state = record.state

    if state == States.MSG_SEND:
        return

    if state == States.NONE:
        record.user.update_tg_id()

    if state == States.AUTH and record.message:
        is_success = send_to_user(
            user_id=record.user.user_tg_id, message=record.message
        )
        send_to_user(user_id=record.user.user_tg_id, message=email_guide)
        send_to_user(user_id=record.user.user_tg_id, message="", image=SKY_DIXY_PATH)
        send_to_user(user_id=record.user.user_tg_id, message=vpn_guide)
        if is_success:
            row = await queries.msg_send(record=data)
            try:
                send_to_itil(Record(**row))
            except Exception:
                logging.exception(f"SEND TO ITIL - Record: {data}")
            return

    await update(data)


def send_to_itil(record: Record):
    state = record.state
    if state == States.MSG_SEND:
        subject = "Событие: чат бот отравил сообщение пользователю"
    elif state == States.AUTH:
        subject = "Событие: пользователь авторизовался в чат боте"
    else:
        return

    text = (
        f"#Табельный номер={record.user_id}#\t\n"
        f"#Номер телефона=7{record.phone}#\t\n"
        f"#Авторизация пользователя в боте (поделиться номером)={str(bool(record.user_tg_id)).lower()}#\t\n"
        f"#Отправлено сообщение={str(bool(record.send_date)).lower()}#\t\n"
        f"#Дата отправки={(record.send_date + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M:%S') if record.send_date else 'null'}#"
    )

    send_mail(ITIL_EMAIL, subject=subject, text=text)


async def handle_order_create(data: OrderCreatedData):
    row = await queries.get(user_id=data.user_id)
    if row:
        row = Record(**row)
        row.update(data)
        data = row

    state = data.state

    if state == States.NONE:
        data.update_tg_id()
        if data.user_tg_id:
            try:
                send_to_itil(data)
            except Exception:
                logging.exception(f"SEND TO ITIL - Record: {data}")

    await update(data)


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
    await Database.get_connection()
    while True:
        imap = await connect()
        while True:
            try:
                await read_messages(imap)
                await asyncio.sleep(DELAY)
            except Exception:
                logging.exception(msg="Error")
                break


if __name__ == "__main__":
    asyncio.run(main())
