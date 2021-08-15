from typing import TypedDict, Optional


class UserInfo(TypedDict):
    user_id: str
    user_tg_id: Optional[str]
    phone: int
    full_name: str
    message: str
