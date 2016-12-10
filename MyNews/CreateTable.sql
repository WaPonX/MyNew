drop database MyNewsDB;

create database MyNewsDB;
use MyNewsDB;

create table MyNews (
    id int unsigned NOT NULL auto_increment primary key,
    url varchar(1024) NOT NULL,
    title varchar(50) NOT NULL UNIQUE,
    tag varchar(20) NOT NULL,
    time char(10) NOT NULL,
    context text NOT NULL,
    cover varchar(1024) NOt NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
