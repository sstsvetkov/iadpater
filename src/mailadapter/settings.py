import logging
from os import environ

DEBUG = environ.get("DEBUG", False)
IMAP_HOST = environ.get("IMAP_HOST")
IMAP_PORT = environ.get("IMAP_PORT")
IMAP_USER = environ.get("IMAP_USER")
IMAP_PASSWD = environ.get("IMAP_PASSWD")
SMTP_FROM = environ.get("SMTP_FROM")
DELAY = int(environ.get("DELAY", 60))
AUTOFAQ_SERVICE_HOST = environ.get("AUTOFAQ_SERVICE_HOST")
ITIL_EMAIL = environ.get("ITIL_EMAIL")

logging.basicConfig(level=logging.INFO)
