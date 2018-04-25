#   coding=utf-8
import fieldtype


class BaseColumn(object):
    def set_name(self,name):
        self.name=name


class Column(BaseColumn):

    def __init__(self,type,default=None,unique=False,is_null=True,doc=''):
        self.type=type
        self.unique=unique
        self.is_null=is_null
        self.name=None
        self.doc=doc
        self.default=default

    def __eq__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}={}'.format(self.name,other)
        else:
            return "{}='{}'".format(self.name, other)

    def __ne__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}!={}'.format(self.name,other)
        else:
            return "{}!='{}'".format(self.name, other)

    def __lt__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}<{}'.format(self.name,other)
        else:
            return "{}<'{}'".format(self.name, other)

    def __gt__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}>{}'.format(self.name,other)
        else:
            return "{}>'{}'".format(self.name, other)

    def __le__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}<={}'.format(self.name,other)
        else:
            return "{}<='{}'".format(self.name, other)

    def __ge__(self, other):
        if isinstance(self.type,fieldtype.Number):
            return '{}>={}'.format(self.name,other)
        else:
            return "{}>='{}'".format(self.name, other)


class ForeignKeyColumn(BaseColumn):
    def __init__(self,parent_table,foreign_key_name=None,backref=None):
        '''
        :param parent_table:类 外键的父表
        :param child_table:类  字表模型类
        :param foreign_key_name: 外键字段名 默认是父表名加个_id example:father_id
        :param backref: 父表引用字表的属性名 默认是子表名加个s  example:users
        '''
        self.p_table_cls=parent_table
        self.p_table=parent_table.__table__
        self.fk_name=foreign_key_name if foreign_key_name else self.p_table+'_id'
        self.backref=backref

    def set_child_table_name(self,name):
        self.c_table=name
        if not self.backref:
            #如果backref为None就设置 父表引用字表的属性名是子表名加个s
            self.backref=name+'s'
        if not hasattr(self.p_table_cls,'fks'):#给父表模型类添加引用字表的属性名
            setattr(self.p_table_cls, 'fks', [])
        getattr(self.p_table_cls,'fks').append(self)

if __name__ == "__main__":
   pass
