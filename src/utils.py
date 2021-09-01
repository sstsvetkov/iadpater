import re


def parse_phone(phone: str) -> int:
    phone = "".join(re.findall(r"\d+", phone))
    if len(phone) < 10:
        raise ValueError
    try:
        phone = int(phone[len(phone) - 10 :])
    except:
        raise ValueError
    return phone
