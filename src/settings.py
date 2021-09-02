import logging
from os import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DEBUG = environ.get("DEBUG", "") == "True"
IMAP_HOST = environ.get("IMAP_HOST")
IMAP_PORT = environ.get("IMAP_PORT")
IMAP_USER = environ.get("IMAP_USER")
IMAP_PASSWD = environ.get("IMAP_PASSWD")
SMTP_FROM = environ.get("SMTP_FROM")
DELAY = int(environ.get("DELAY", 60))
AUTOFAQ_SERVICE_HOST = environ.get("AUTOFAQ_SERVICE_HOST")
ITIL_EMAIL = environ.get("ITIL_EMAIL")
AD = environ.get("AD")
SECRET = environ.get("SECRET")

# ITILIUM
ITIL_API_URL = environ.get("ITIL_API_URL")
ITIL_PASS = environ.get("ITIL_PASS")
ITIL_LOGIN = environ.get("ITIL_LOGIN")

if DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
