# _*_ coding: utf-8 _*_
# @Time    : 2017/11/3 下午4:12
# @Author  : 杨楚杰
# @File    : pg_client.py
# @license : Copyright(C), 安锋游戏
from io import StringIO
import redis
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool


class pg_client:
    def __init__(self, host, port, database, username, password):
        uri = "postgresql://{username}:{password}@{host}:{port}/{database}"\
            .format(host=host, port=port, database=database, username=username, password=password)
        self.engine = create_engine(uri, echo=False, pool_recycle=5, pool_size=1, poolclass=SingletonThreadPool)
        self.db_session = sessionmaker(autocommit=True, bind=self.engine)

    def query(self, sql):
        result = self.db_session().execute(sql).fetchall()
        return result

    def query_for_count(self, sql):
        return self.db_session().execute(sql).scalar()

    def execute(self, sql):
        _session = self.db_session()
        _session.begin()
        try:
            result = _session.execute(sql)
            _session.commit()
            return result.rowcount
        except Exception as e:
            import traceback
            _session.rollback()
            return -1
        finally:
            _session.close()

    # SQL方式导入从文件导出到文件
    def copy_file(self, copy_sql, file):
        conn = self.engine.raw_connection()
        cur = conn.cursor()
        cur.copy_expert(copy_sql, file)
        conn.commit()
        cur.close()

    # 多条从read(), readline()流中导入数据
    def copy_file_to_table(self, file, table, columns=(), sep=',', null='\\N'):
        conn = self.engine.raw_connection()
        cur = conn.cursor()
        cur.copy_from(file, table, sep=sep, null=null, columns=columns)
        conn.commit()
        cur.close()

    '''
    导出数据到文件,包含表头
    table:  gp/pg 中的表名称
    file: 一个csv文件
    sep: 导出文件分隔符
    '''
    def export_to_file(self, table, file, sep=',', is_header=False):

        fileObj = open(file, 'wb')

        is_header = 'HEADER' if is_header else ''

        self.copy_file("COPY %s TO STDOUT WITH CSV %s DELIMITER as '%s' NULL as '\\N' ESCAPE as '\\'"
                       % (table, is_header, sep), fileObj)

    '''
        导入数据从CSV文件, 不包含表头
        table:  gp/pg 中的表名称
        file: 一个csv文件
        sep: 导入文件字段分隔符
    '''
    def import_from_file(self, table, fileName, sep=',', is_header=False):

        fileObj = open(fileName, encoding="utf-8")

        is_header = 'HEADER' if is_header else ''

        self.copy_file("COPY %s FROM STDIN WITH CSV %s DELIMITER as '%s' NULL as '\\N' ESCAPE as '\\'"
                       % (table, is_header, sep), fileObj)

    '''
      file: 一个能够使用read(), readline()的流数据
      columns:  ('col1', 'col2'....)
    '''
    def import_from_io(self, table, fileStr, columns, sep=','):
        line = StringIO(fileStr)
        self.copy_file_to_table(line, table, columns=columns, sep=sep)

    def get_session(self):
        return self.db_session()


class mysql_client:
    def __init__(self, host, port, database, username, password):
        uri = "mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8"\
            .format(host=host, port=port, database=database, username=username, password=password)
        self.engine = create_engine(uri, echo=False, pool_recycle=5, poolclass=SingletonThreadPool)
        self.db_session = sessionmaker(autocommit=True, bind=self.engine)

    def query(self, sql):
        result = self.db_session().execute(sql).fetchall()
        return result

    def query_for_count(self, sql):
        return self.db_session().execute(sql).scalar()

    def execute(self, sql):
        _session = self.db_session()
        _session.begin()
        try:
            result = _session.execute(sql)
            _session.commit()
            return result.rowcount
        except Exception as e:
            _session.rollback()
            print("exec sql exception - %s" % (e,))
            return 0
        finally:
            _session.close()

    def get_session(self):
        return self.db_session()


class redis_client:
    def __init__(self, host, port, db, key_prefix):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db)
        self.redis = redis.Redis(connection_pool=self.pool)
        self.key_prefix = key_prefix

    # 添加数据并返回添加后的数据总数
    def append_to_list(self, key, value):
        key = "%s_%s" % (self.key_prefix, key)
        return self.redis.rpush(key, value)

    # 获取列表数据
    def get_list_data(self, key):
        key = "%s_%s" % (self.key_prefix, key)
        data_list = self.redis.lrange(key, 0, -1)
        sql_list = []
        for item in data_list:
            sql_list.append(item.decode(encoding='utf-8'))
        self.redis.delete(key)
        return sql_list

    def set_kv(self, key, value):
        self.redis.set(key, value)

    def get_value(self, key):
        return self.redis.get(key)

    def set(self, key, value):
        key = "%s_%s" % (self.key_prefix, key)
        return self.redis.set(key, value)

    def get(self, key):
        key = "%s_%s" % (self.key_prefix, key)
        return self.redis.get(key)

    def delete(self, key):
        key = "%s_%s" % (self.key_prefix, key)
        return self.redis.delete(key)
