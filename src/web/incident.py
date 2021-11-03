# create table orders
# (
#     row_id SERIAL NOT NULL PRIMARY KEY,
#     order_id varchar(64) NOT NULL,
#     user_tg_id varchar(64) NOT NULL,
#     status varchar(16) NOT NULL
# );


class Incident:
    incident_uid: str
    user_tg_id: str
    status: str

    def __init__(self, incident_uid, user_tg_id, status, *args, **kwargs):
        self.incident_uid = incident_uid
        self.user_tg_id = user_tg_id
        self.status = status
