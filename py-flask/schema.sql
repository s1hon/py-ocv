drop table if exists prints;
create table prints (
  id integer primary key autoincrement,
  create_time datetime default (datetime('now','localtime')),
  print_id CHAR(6) UNIQUE not null,
  stu_id CHAR(10) not null,
  name string not null,
  phone CHAR(10) not null,
  status int not null
);
