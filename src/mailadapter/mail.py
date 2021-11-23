import logging
import smtplib
from email.header import decode_header, Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from re import search

from settings import (
    SMTP_FROM,
    IMAP_HOST,
)
from mailadapter.user_info import Record
from mailadapter.utils import parse_phone


def parse_email_closed(body: str) -> Record or ValueError:
    try:
        result = search(
            ".*Табельный номер:(.*)\r*\n*.*ФИО:(.*)\r*\n*.*Номер телефона:(.*)\r*\n*",
            body,
        )
        user_id = result.group(1).strip()
        fio = result.group(2).strip()
        try:
            phone = str(parse_phone(result.group(3).strip()))
        except ValueError or AttributeError:
            phone = None
        msg = (
            body.split("---------------------------", 1)[1]
            .replace("Ответственный", "\nОтветственный")
            .replace("Наряд", "\nНаряд")
            .replace("Решение", "\nРешение")
        )
        record = Record(user_id=user_id, phone=phone, full_name=fio, message=msg)
        logging.debug(f"PARSING Raw: {body} Result: {record}")
        return record
    except Exception as e:
        logging.exception(f"PARSING Raw: {body}")
        raise ValueError from e


# Предоставить набор стандартных доступов Веденеев Дмитрий Витальевич, Дикси МО-Запад, ДЮ-276910, Региональный менеджер
def parse_email_created(body: str) -> Record or ValueError:
    try:
        result = search(
            "Предоставить набор стандартных доступов(.*),(.*),(.*),(.*)", body
        )
        user_id = result.group(3).strip()
        fio = result.group(1).strip()

        record = Record(user_id=user_id, full_name=fio)
        logging.debug(f"PARSING - Raw: {body} Result: {record}")
        return record
    except Exception as e:
        logging.exception(f"PARSING - Raw: {body}")
        raise ValueError from e


def parse_work_group_notification(body: str) -> str or ValueError:
    return body


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


def send_mail(toaddrs, subject, text):
    fromaddr = SMTP_FROM
    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = fromaddr
    msg["To"] = toaddrs
    body = MIMEText(_text=text, _subtype="plain", _charset="utf-8")
    msg.attach(body)
    try:
        server = smtplib.SMTP(IMAP_HOST)
        server.sendmail(fromaddr, toaddrs, msg.as_string())
        server.quit()
        logging.debug(
            f"SMTP SEND - From: {fromaddr} To: {toaddrs} Subject: {subject} Msg: {text}"
        )
    except Exception as e:
        logging.exception(
            f"SMTP SEND - From: {fromaddr} To: {toaddrs} Subject: {subject} Msg: {text}"
        )
