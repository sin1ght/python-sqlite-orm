#   coding=utf8
from functools import wraps
from config import Config
import sqlite3
import fieldtype
from column import Column,ForeignKeyColumn


def is_exist_table(func):
    '''
    判断数据库是否已经创建表
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        table=args[0].__table__
        mapping=args[0].__mapping__
        foreign_key=args[0].__foreign_key__
        if table and mapping:
            db_name = Config.database
            conn = sqlite3.connect(db_name)
            params = ""
            foreign_key_str=[]
            for k, v in mapping.iteritems():
                if isinstance(v,Column):
                    unique = "unique" if v.unique else ""
                    is_null = "" if v.is_null else "not null"
                    if isinstance(v.type, fieldtype.Number):
                        default = 'default {}'.format(v.default) if v.default else ''
                    else:
                        default = "default '{}'".format(v.default) if v.default else ''
                    params += "{} {} {} {} {},".format(k, v.type, default, unique, is_null)
                elif isinstance(v,ForeignKeyColumn):
                    p_table=v.p_table
                    fk_name=v.fk_name
                    params+="{} integer,".format(fk_name)
                    foreign_key_str.append('foreign key ({}) references {}(id) on delete cascade)'.format(fk_name,p_table))
            params = params[:-1]  # 去掉最后的逗号
            if not foreign_key:
                sql = "create table if not exists {}(id INTEGER PRIMARY KEY AUTOINCREMENT,{})".format(table, params)
            else:
                sql = "create table if not exists {}(id INTEGER PRIMARY KEY AUTOINCREMENT,{},{}".format(table, params,','.join(foreign_key_str))
            conn.execute(sql)
            conn.commit()
            kwargs['__conn'] =conn
            kwargs['__table']=table
            kwargs['__mapping']=mapping
            r=func(*args, **kwargs)
            conn.close()
            return r
        else:
            print "not exist __table__ or __mapping__"
    return decorated_function

