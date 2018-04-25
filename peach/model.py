#   coding=utf8
from column import Column,BaseColumn,ForeignKeyColumn
from decorators import is_exist_table
import sqlite3
from config import Config
from fieldtype import Integer


class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
        else:
            name=name.lower()
            mapping={} #保存表的字段映射
            has_foreign_key=False
            for k,v in attrs.iteritems():
                if isinstance(v,BaseColumn):
                    mapping[k]=v
                    v.set_name(k)
                if isinstance(v,ForeignKeyColumn):
                    v.set_child_table_name(name)
                    has_foreign_key=True
            attrs['id']=Column(Integer()) #默认添加id为主键
            attrs['id'].set_name('id')
            attrs['__mapping__']=mapping #类属性
            attrs['__table__']=name
            attrs['__foreign_key__']=has_foreign_key
            return type.__new__(cls, name, bases, attrs)


class Model(object):
    __metaclass__ = ModelMetaclass

    def __init__(self,**kwargs):
        setattr(self,'id',kwargs.get('id'))
        for k in self.__mapping__.keys():
            setattr(self,k,kwargs.get(k))

    @classmethod
    def get_child_cls_by_name(cls,name):
        for child in cls.__subclasses__():
            if name==child.__name__:
                return child

    @is_exist_table
    def save(self,update=False,**kwargs):
        table=kwargs['__table']
        conn=kwargs['__conn']
        mapping=kwargs['__mapping']
        if not update: #不更新就存储
            fields = []
            params = []
            args = []
            for k,v in mapping.iteritems():
                value=getattr(self, k, None)
                if isinstance(v,ForeignKeyColumn):
                    # 是外键
                    fields.append(v.fk_name)
                    params.append('?')
                    args.append(value.id)
                else:
                    if v.default and not value:
                        # 如果value为none且此字段有默认值 就不插入此字段
                        pass
                    else:
                        fields.append(k)
                        params.append('?')
                        args.append(value)
            sql = 'insert into %s (%s) values (%s)' % (table, ','.join(fields), ','.join(params))
            conn.execute(sql,tuple(args))
        else:
            params=[]
            for k in mapping.keys():
                v=getattr(self,k,None)
                if v:
                    params.append("{}='{}'".format(k,v))
            sql='update {} set {} where id={}'.format(table,','.join(params),self.id)
            conn.execute(sql)
            pass
        conn.commit()

    @classmethod
    @is_exist_table
    def select(cls,columns=None,**kwargs):
        '''
        :param columns: 选择的要查询的列名 列表
        :return:
        '''
        table = kwargs['__table']
        _columns=[]
        _columns.append('id') #始终查询id字段 方便更新 和删除
        if not columns:#columns为None 就查询所有字段
            mapping = kwargs['__mapping']
            for k,v in mapping.iteritems():
                if isinstance(v,Column):
                    _columns.append(k)
                elif isinstance(v,ForeignKeyColumn):
                    _columns.append(v)
        else:
            for v in columns:
                if isinstance(v,Column):
                    _columns.append(v.name)
                elif isinstance(v,ForeignKeyColumn):
                    _columns.append(v)
        return Query(cls,table,_columns)

    @classmethod
    @is_exist_table
    def delete(cls,**kwargs):
        table = kwargs['__table']
        sql='delete from {}'.format(table)
        return Delete(sql)

    @classmethod
    @is_exist_table
    def update(cls,columns,values,**kwargs):
        '''
        :param columns: 更新的字段列表 User.name
        :param values: 对应字段的值列表
        :return:
        '''
        table = kwargs['__table']
        params=[]
        for i in range(len(columns)):
            params.append("{}='{}'".format(columns[i].name,values[i]))
        sql = 'update {} set {}'.format(table,','.join(params))
        return Update(sql)


class BaseSQLModel(object):
    def __init__(self):
        self._conn = sqlite3.connect(Config.database)  # 数据库连接对象
        self._where = ''
        self._sql=''

    def where(self,*expressions):
        if self._where:#where不为空 多次调用where用 or 连接
            self._where+=' or '
        self._where += '('
        for item in expressions:
            self._where += (item + ' and ')
        self._where = self._where[:-5]  # 去掉最后的 ' and '
        self._where += ')'
        return self

    def excute(self):
        if self._where:
            self._sql += ' where {}'.format(self._where)
        self._conn.execute(self._sql)
        self._conn.commit()
        self._conn.close()


class Update(BaseSQLModel):
    def __init__(self,sql):
        super(Update, self).__init__()
        self._sql = sql


class Delete(BaseSQLModel):
    def __init__(self,sql):
        super(Delete, self).__init__()
        self._sql=sql


class Query(BaseSQLModel):
    def __init__(self,obj,table,columns):
        super(Query, self).__init__()
        self._obj=obj #模型类
        self._table=table
        self._columns=columns
        self._group_by=''
        self._order_by = ''
        self._limit=''
        self._offset=''

    def group_by(self,field):
        self._group_by+='group by '+field.name
        print 'group_by:{}'.format(self._group_by)
        return self

    def order_by(self,field,desc=False):
        '''
        :param field: 字段(模型类属性)User.name
        :param desc: 默认升序
        :return:
        '''
        self._order_by += field.name
        if desc:
            self._order_by += ' desc'
        print 'order_by:{}'.format(self._order_by)
        return self

    def limit(self,num):
        self._limit+='limit '+str(num)
        print 'limit:{}'.format(self._limit)
        return  self

    def offset(self,index):
        self._offset+='offset '+str(index)
        print 'offset:{}'.format(self._offset)
        return self

    def all(self):
        cols=[]
        for i in self._columns:
            if isinstance(i,ForeignKeyColumn):
                cols.append(i.fk_name)
            else:
                cols.append(i)
        self._sql='select {} from {}'.format(','.join(cols),self._table)
        if self._where:
            self._sql+=' where {}'.format(self._where)
        if self._group_by:
            self._sql+=' '+self._group_by
        if self._order_by:
            self._sql+=' order by {}'.format(self._order_by)
        if self._limit:
            self._sql+=' '+self._limit
        if self._offset:
            self._sql+=' '+self._offset
        cursor=self._conn.cursor()
        cursor.execute(self._sql)
        self._conn.commit()
        data=cursor.fetchall()

        objs=[]
        for item in data:
            obj=self._obj()
            for attr_value in item:
                attr_name=self._columns[item.index(attr_value)]
                if isinstance(attr_name,ForeignKeyColumn):
                    setattr(obj,attr_name.name,attr_name.p_table_cls.select().where('id='+str(attr_value)).__first())
                else:
                    setattr(obj,attr_name,attr_value)
            if hasattr(self._obj,'fks'):
                #如果是父表就把所有字表关联数据参训出来
                for fk in getattr(self._obj,'fks'):
                    child_cls=Model.get_child_cls_by_name(fk.c_table)
                    child_data=child_cls.select().where('{}={}'.format(fk.fk_name,obj.id)).__all()
                    setattr(obj,fk.backref,child_data)
            objs.append(obj)
        self._conn.close()
        return objs

    def first(self):
        objs=self.all()
        if len(objs)>=1:
            return objs[0]
        else:
            return None

    def __all(self):
        cols = []
        for i in self._columns:
            if isinstance(i, ForeignKeyColumn):
                pass
            else:
                cols.append(i)
        self._sql = 'select {} from {}'.format(','.join(cols), self._table)
        if self._where:
            self._sql += ' where {}'.format(self._where)
        if self._group_by:
            self._sql += ' ' + self._group_by
        if self._order_by:
            self._sql += ' order by {}'.format(self._order_by)
        if self._limit:
            self._sql += ' ' + self._limit
        if self._offset:
            self._sql += ' ' + self._offset
        cursor = self._conn.cursor()
        cursor.execute(self._sql)
        self._conn.commit()
        data = cursor.fetchall()
        objs = []
        for item in data:
            obj = self._obj()
            for attr_value in item:
                attr_name = self._columns[item.index(attr_value)]
                if isinstance(attr_name, ForeignKeyColumn):
                    pass
                else:
                    setattr(obj, attr_name, attr_value)
            objs.append(obj)
        self._conn.close()
        return objs

    def __first(self):
        objs = self.__all()
        if len(objs) >= 1:
            return objs[0]
        else:
            return None