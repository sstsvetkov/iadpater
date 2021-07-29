create table users
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) NOT NULL UNIQUE,
    email     varchar(128) NOT NULL,
    full_name varchar(128) NOT NULL,
    position  varchar(64),
	last_auth timestamp not null default current_timestamp
);

create table phones
(
    id SERIAL NOT NULL PRIMARY KEY,
    user_id varchar(64) NOT NULL UNIQUE,
    phone   varchar(16) NOT NULL,
    creation_date timestamp not null default current_timestamp
)