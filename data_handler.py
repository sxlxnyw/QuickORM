# coding: utf-8

import MySQLdb
import datetime

class Field(object):
    pass


class Expr(object):
    def __init__(self, model, kwargs):
        self.model = model
        # How to deal with a non-dict parameter?
        self.where = kwargs
        self.params = kwargs.values()
        equations = ['`'+key + '` = %s' for key in kwargs.keys()]
        self.where_expr = 'where ' + ' and '.join(equations) if len(equations) > 0 else ''
        self.limit_expr = ""

    def update(self, **kwargs):
        _keys = []
        _params = []
        for key, val in kwargs.iteritems():
            if key == "updated_at":
                continue
            if val is None or key not in self.model.fields:
                continue
            _keys.append(key)
            _params.append(val)
        if "updated_at" in self.model.fields:
            _keys.append("updated_at")
            _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        _params.extend(self.params)
        sql = 'update `%s` set %s %s;' % (
            self.model.table_name(), ', '.join(['`'+key + '` = %s' for key in _keys]), self.where_expr)
        return Database.execute(sql, _params).rowcount

    def upsert(self, **kwargs):
        count = self.count()
        if count > 0:
            return self.update(**kwargs)
        else:
            _keys = []
            _params = []
            for key, val in kwargs.iteritems():
                if val is None or key == "updated_at" or key == "created_at" or key not in self.model.fields:
                    continue
                _keys.append(key)
                _params.append(val)
            for key, val in self.where.iteritems():
                if val is None or key == "updated_at" or key == "created_at" or key not in self.model.fields:
                    continue
                _keys.append(key)
                _params.append(val)
            if "updated_at" in self.model.fields:
                _keys.append("updated_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if "created_at" in self.model.fields:
                _keys.append("created_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            insert = 'insert ignore into %s(%s) values (%s);' % (
                self.model.table_name(), ', '.join(_keys), ', '.join(['%s'] * len(_keys)))
            return Database.execute(insert, _params).rowcount

    def selectsert(self, **kwargs):
        row = self.select_one()
        if row is None:
            _keys = []
            _params = []
            for key, val in kwargs.iteritems():
                if val is None or key == "updated_at" or key == "created_at" or key not in self.model.fields:
                    continue
                _keys.append(key)
                _params.append(val)
            for key, val in self.where.iteritems():
                if val is None or key == "updated_at" or key == "created_at" or key not in self.model.fields:
                    continue
                _keys.append(key)
                _params.append(val)
            if "updated_at" in self.model.fields:
                _keys.append("updated_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if "created_at" in self.model.fields:
                _keys.append("created_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            insert = 'insert ignore into %s(%s) values (%s);' % (
                self.model.table_name(), ', '.join(_keys), ', '.join(['%s'] * len(_keys)))
            Database.execute(insert, _params)
            row = self.select_one()
        return row

    def limit(self, rows, offset=None):
        self.limit_expr = ' limit %s%s' % (
            '%s, ' % offset if offset is not None else '', rows)
        return self

    def select(self):
        sql = 'select `%s` from `%s` %s %s;' % ('`,`'.join(self.model.fields.keys()), self.model.table_name(), self.where_expr, self.limit_expr)
        for row in Database.execute(sql, self.params).fetchall():
            inst = self.model()
            for idx, f in enumerate(row):
                setattr(inst, self.model.fields.keys()[idx], f)
            yield inst

    def count(self):
        sql = 'select count(*) from `%s` %s %s;' % (self.model.table_name(), self.where_expr, self.limit_expr)
        (row_cnt, ) = Database.execute(sql, self.params).fetchone()
        return row_cnt

    def select_one(self):
        self.limit(1)
        sql = 'select `%s` from `%s` %s %s;' % ('`,`'.join(self.model.fields.keys()), self.model.table_name(), self.where_expr, self.limit_expr)
        row = Database.execute(sql, self.params).fetchone()
        if row:
            inst = self.model()
            for idx, f in enumerate(row):
                setattr(inst, self.model.fields.keys()[idx], f)
            return inst
        return None


class MetaModel(type):
    db_table = None
    fields = {}

    def __init__(cls, name, bases, attrs):
        super(MetaModel, cls).__init__(name, bases, attrs)
        fields = {}
        for key, val in cls.__dict__.iteritems():
            if isinstance(val, Field):
                fields[key] = val
        cls.fields = fields
        cls.attrs = attrs


class Model(object):
    __metaclass__ = MetaModel

    def save(self):
        _keys = []
        _params = []
        if "id" in self.__dict__.keys():
            for key, val in self.__dict__.iteritems():
                if key == "updated_at" or key == "created_at" or key == "id":
                    continue
                _keys.append(key)
                _params.append(val)
            if "updated_at" in self.fields:
                _keys.append("updated_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            update = 'update `%s` set %s where id=%s;' % (
                self.table_name(), ','.join(['`'+key + '` = %s' for key in _keys]), self.id)
            Database.execute(update, _params)
        else:
            for key, val in self.__dict__.iteritems():
                if key == "updated_at" or key == "created_at":
                    continue
                _keys.append(key)
                _params.append(val)
            if "created_at" in self.fields:
                _keys.append("created_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if "updated_at" in self.fields:
                _keys.append("updated_at")
                _params.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            insert = 'insert ignore into `%s`(`%s`) values (%s);' % (
                self.table_name(), '`,`'.join(_keys), ', '.join(['%s'] * len(_keys)))
            Database.execute(insert, _params)
            (self.id, ) = Database.execute('SELECT LAST_INSERT_ID()').fetchone()

    @classmethod
    def where(cls, **kwargs):
        return Expr(cls, kwargs)
    
    @classmethod
    def table_name(cls):
        return cls.db_table


class Database(object):
    autocommit = True
    conn = None
    db_config = {}

    @classmethod
    def connect(cls, **db_config):
        cls.conn = MySQLdb.connect(host=db_config.get('host', 'localhost'), port=int(db_config.get('port', 3306)),
                                   user=db_config.get('user', 'root'), passwd=db_config.get('password', ''),
                                   db=db_config.get('database', 'test'), charset=db_config.get('charset', 'utf8'))
        cls.conn.autocommit(cls.autocommit)
        cls.db_config.update(db_config)

    @classmethod
    def get_conn(cls):
        if not cls.conn or not cls.conn.open:
            cls.connect(**cls.db_config)
        try:
            cls.conn.ping()
        except MySQLdb.OperationalError:
            cls.connect(**cls.db_config)
        return cls.conn

    @classmethod
    def execute(cls, *args):
        cursor = cls.get_conn().cursor()
        cursor.execute(*args)
        return cursor

    def __del__(self):
        if self.conn and self.conn.open:
            self.conn.close()


def execute_raw_sql(sql, params=None):
    return Database.execute(sql, params) if params else Database.execute(sql)

def main():
   print "we are in %s"%__name__

if __name__ == '__main__':
  main()
