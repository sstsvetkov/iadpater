create table users
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) NOT NULL UNIQUE,
    email     varchar(128) NOT NULL,
    full_name varchar(128) NOT NULL,
    position  varchar(64),
    phone   varchar(16),
	last_auth timestamp not null default current_timestamp
);

create table phones
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) NOT NULL UNIQUE,
    phone   varchar(16) NOT NULL,
    creation_date timestamp not null default current_timestamp
);

create table records
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) UNIQUE NOT NULL,
    user_tg_id varchar(64),
    message varchar(2048),
    phone   varchar(16),
    full_name varchar(128),
    send_date timestamp
);

create table incidents
(
    row_id SERIAL NOT NULL PRIMARY KEY,
    incident_uid varchar(64) NOT NULL UNIQUE,
    user_tg_id varchar(64) NOT NULL,
    status varchar(64) NOT NULL
);