import asyncio
import imaplib
from datetime import timedelta
from email.parser import BytesParser

from mailadapter import *
from mailadapter.user_info import Record, States

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
                record: Record = parse_email_closed(body)
                await handle_order_closed(record)
            except ValueError:
                pass

        elif "Зарегистрировано Обр." in subject:
            body = get_email_body(msg)
            try:
                record: Record = parse_email_created(body)
                await handle_order_create(record)
            except ValueError:
                pass
    imap.expunge()


async def handle_order_closed(record: Record):
    row = await queries.get(user_id=record.user_id)
    if row:
        row = Record(**row)
        row.update(record)
        record = row

    if record.state == States.MSG_SEND:
        return

    if record.state == States.NONE:
        record.update_tg_id()

    if record.state == States.AUTH and record.message:
        is_success = send_to_user(user_id=record.user_tg_id, message=record.message)
        send_to_user(user_id=record.user_tg_id, message=email_guide)
        send_to_user(user_id=record.user_tg_id, message="", image=SKY_DIXY_PATH)
        send_to_user(user_id=record.user_tg_id, message=vpn_guide)
        if is_success:
            row = await queries.msg_send(record=record)
            try:
                send_to_itil(Record(**row))
            except Exception:
                logging.exception(f"SEND TO ITIL - Record: {record}")
            return

    await update(record)


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


async def handle_order_create(record: Record):
    row = await queries.get(user_id=record.user_id)
    if row:
        row = Record(**row)
        row.update(record)
        record = row

    state = record.state

    if state == States.NONE:
        record.update_tg_id()
        if record.user_tg_id:
            try:
                send_to_itil(record)
            except Exception:
                logging.exception(f"SEND TO ITIL - Record: {record}")

    await update(record)


# async def connect():
#     for attempt in range(3):
#         try:
#             imap = imaplib.IMAP4_SSL(IMAP_HOST, port=IMAP_PORT)
#             imap.login(IMAP_USER, IMAP_PASSWD)
#             logging.info("Connecting to mail server")
#             return imap
#         except Exception as e:
#             if attempt == 2:
#                 raise e
#             await asyncio.sleep(DELAY * 2)


async def main():
    while True:
        try:
            await Database.get_connection_pool()
            logging.info("DB connected successfully")
            imap = imaplib.IMAP4_SSL(IMAP_HOST, port=IMAP_PORT)
            imap.login(IMAP_USER, IMAP_PASSWD)
            logging.info("Mail server connected successfully")
            try:
                await read_messages(imap)
            except Exception:
                logging.exception(msg="Error")
            imap.close()
            imap.logout()
        except Exception:
            logging.exception(msg="Error")
        await asyncio.sleep(DELAY)


if __name__ == "__main__":
    asyncio.run(main())
