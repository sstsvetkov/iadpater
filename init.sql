create table users
(
    phone     varchar(16),
    email     varchar(128) NOT NULL,
    full_name varchar(128) NOT NULL,
    position  varchar(64),
	last_auth timestamp not null default current_timestamp
);