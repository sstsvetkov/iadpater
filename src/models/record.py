from src.models.model import Model

"""
row_id SERIAL NOT NULL PRIMARY KEY,
user_id varchar(64),
user_tg_id varchar(64),
message varchar(2048),
phone   varchar(16),
full_name varchar(128),
creation_date timestamp not null default current_timestamp
"""


class Record(Model):
    fields = [
        "user_id",
        "user_tg_id",
        "message",
        "phone",
        "full_name",
        "creation_date",
    ]
    pk = ["row_id"]

    uniques = [
        "user_id"
    ]

    table_name = "Records"

    def __init__(
        self,
        row_id=None,
        user_id=None,
        user_tg_id=None,
        message=None,
        phone=None,
        full_name=None,
        creation_date=None,
    ):
        super(Record, self).__init__()
        self.row_id = row_id
        self.user_id = user_id
        self.user_tg_id = user_tg_id
        self.message = message
        self.phone = phone
        self.full_name = full_name
        self.creation_date = creation_date
