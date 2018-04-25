# python-sqlite-orm
一个简单的python sqlite orm

### Exmaples:
首次使用操作数据库的方法时（save，update，select，delete）自动创建表

自动创建主键id，自增

* 插入
```python
from peach import *
from peach import fieldtype


class Article(Model):
    name=Column(fieldtype.String(20))
    price=Column(fieldtype.Float(),default=11.0,is_null=False)

if __name__ == "__main__":
    SqliteDatabase('test.db')

    a=Article(name='c++')
    a.save()

```
* 查询
```python
#first()返回单个对象
#all()返回对象列表
a=Article.select([Article.name]).where(Article.id==1).first()
a.name

#select()无参数则查询所有字段 默认总是查询id字段
b=Article.select().where(Article.price>=10).all()

#同一个where里面的表达式用and连接 不同where之间是 or连接
Article.select().where(Article.name=='c++',Article.price<=20).where(Article.id==2).all()

#limit order_by offset也支持
Article.select().order_by(Article.price,desc=True).limit(1).offset(1).all()
```
* 更新
```python
#通过调用查询出来的对象的save()
a=Article.select().where(Article.id==1).first()
a.price=19
a.save(update=True)

#通过update（）
Article.update([Article.name,Article.price],['php',15.63]).where(Article.id==1).excute()
```
* 删除
```python
Article.delete().where(Article.id==1).excute()
```

* 一对多 外键
```python
from peach import *
from peach import fieldtype


class Author(Model):
    name=Column(fieldtype.String(20))
    age=Column(fieldtype.Integer())


class Book(Model):
    name = Column(fieldtype.String(20))
    price= Column(fieldtype.Float())
    author=ForeignKeyColumn(Author)

if __name__ == "__main__":
    SqliteDatabase('test.db')

    a=Author.select().where(Author.id==1).first()
    book=Book(name='c++',price=12.3,author=a)
    book.save()
    
    #查询时可直接访问author属性
    b=Book.select().where(Book.id==2).first()
    print b.author
    
    #父表访问backref属性  是个对象列表 backref默认时字表名加个s 可以在设置外键列的时候传递参数设置
    a=Author.select().where(Author.id==1).first()
    print a.books
  
```
