QuickORM
========

A simple ORM provides elegant API for Python-MySQL operation

Connect to MySQL
----------------

```python
from data_handler import Database

db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'test'
}
Database.connect(**db_config)
```

Define a model
--------------

```python
from data_handler import Model, Field

class TestModel(Model):
  db_table = 'test'
  a = Field()
  b = Field()
```

Insert
------

```python
test = TestModel()
test.a = 5
test.b = 'john'
test.save()
```

Query
-----

```python
for r in TestModel.where(a=5, b='john').select():
  print r.a
  print r.b
```

Count
-----

```python
print TestModel.where(a=5, b='john').count()
```

Update
------

```python
TestModel.where(a=5, b='john').update(a=1)
```

Execute raw SQL
---------------

```python
from data_handler import execute_raw_sql

results = execute_raw_sql('select b, count(*) from test where b = %s group by b;', (1,))
for val, cnt in results:
  print val, cnt
```

Connection pool
---------------
http://blog.csdn.net/zbc1090549839/article/details/51336458


Sub table
---------------
http://www.yiichina.com/topic/2531

```SQL
select `TABLE_NAME` from `INFORMATION_SCHEMA`.`TABLES` where `TABLE_SCHEMA`='dbname' and `TABLE_NAME`='tbname' 

CREATE TABLE IF NOT EXISTS `student` (#判断这张表是否存在，若存在，则跳过创建表操作，  
 `s_id` varchar(40) NOT NULL,   
`s_name` varchar(255) default NULL,   
`s_age` varchar(255) default NULL,   
`s_msg` varchar(255) default NULL,   
PRIMARY KEY (`s_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;  
INSERT INTO `student` VALUES ('7', '重阳节', '33', '登高赏菊');  
```
