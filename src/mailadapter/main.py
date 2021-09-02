import asyncio
import imaplib
import logging
from datetime import timedelta, datetime
from email.parser import BytesParser

from mailadapter.chat_bot import send_to_user
from mailadapter.mail import (
    decode_email_header,
    get_email_body,
    parse_email_closed,
    parse_email_created,
    OrderClosedData,
    OrderCreatedData,
    send_mail,
)
from models import Database
from models.record import Record, States
from models.user import User
from settings import (
    BASE_DIR,
    DELAY,
    IMAP_HOST,
    IMAP_PASSWD,
    IMAP_USER,
    IMAP_PORT,
    ITIL_EMAIL,
)

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


def send_info_to_user(record: Record):
    is_success = send_to_user(user_id=record.user.user_tg_id, message=record.message)
    send_to_user(user_id=record.user.user_tg_id, message=email_guide)
    send_to_user(user_id=record.user.user_tg_id, message="", image=SKY_DIXY_PATH)
    send_to_user(user_id=record.user.user_tg_id, message=vpn_guide)
    return is_success


async def handle_order_closed(data: OrderClosedData):
    record: Record = await Record.query_set.get(user_id=data["user_id"])
    if record:
        if data["phone"]:
            record.user.phone = data["phone"]
        record.user.full_name = data["full_name"]
        record.message = data["message"]
    else:
        record = Record(user=User(**data), message=data["message"])

    state = record.state

    if state == States.MSG_SEND:
        return

    if state == States.NONE:
        record.user.update_tg_id()

    if state == States.AUTH and record.message:
        if send_info_to_user(record=record):
            record.send_date = datetime.now()
            if send_to_itil(record):
                record.itil_send_date = datetime.now()

    await record.save()


def send_to_itil(record: Record) -> bool:
    state = record.state
    if state == States.MSG_SEND:
        subject = "Событие: чат бот отравил сообщение пользователю"
    elif state == States.AUTH:
        subject = "Событие: пользователь авторизовался в чат боте"
    else:
        return False

    text = (
        f"#Табельный номер={record.user.user_id}#\t\n"
        f"#Номер телефона=7{record.user.phone}#\t\n"
        f"#Авторизация пользователя в боте (поделиться номером)={str(bool(record.user.user_tg_id)).lower()}#\t\n"
        f"#Отправлено сообщение={str(bool(record.send_date)).lower()}#\t\n"
        f"#Дата отправки={(record.send_date + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M:%S') if record.send_date else 'null'}#"
    )

    return send_mail(ITIL_EMAIL, subject=subject, text=text)


async def handle_order_create(data: OrderCreatedData):
    record: Record = await Record.get(user_id=data["user_id"])
    if record:
        record.user.full_name = data["user_id"]
    else:
        record = Record(user=User(**data))

    state = record.state

    if state == States.NONE:
        if record.user.update_tg_id():
            if send_to_itil(record=record):
                record.itil_send_date = datetime.now()
    await record.save()


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
