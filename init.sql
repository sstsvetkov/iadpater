create table users
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) NOT NULL UNIQUE,
    email     varchar(128),
    full_name varchar(128),
    position  varchar(64),
    phone   varchar(16),
    extra_phone   varchar(16),
    user_tg_id varchar(64),
	last_auth timestamp
);

create table records
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    user_fk int,
    message varchar(2048),
    send_date timestamp,
    itil_send_date timestamp,
    FOREIGN KEY (user_fk) REFERENCES users (row_id)
);