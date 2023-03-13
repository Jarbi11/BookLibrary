# -*- coding: utf-8 -*-

from app import app, db
from app.models import User, Book, Log, Role

app_ctx = app.app_context()
app_ctx.push()
db.create_all()
Role.insert_roles()

new_users = [
    User(name=u'lib_admin', email='admin@library.com', password='admin_lib', major='administrator',
         headline=u"admin", about_me=u"admin"),

    User(name=u'test0', email='test0@test.com', password='123456', role_id=3),
    User(name=u'test1', email='test1@test.com', password='123456', role_id=2),
    User(name=u'test2', email='test2@test.com', password='123456', role_id=1),
]
new_books = [
    Book(title=u"STL源码剖析", author=u"侯捷", isbn='9787560926995',
         tags_string=u"计算机,程序设计,C++", image='http://img3.doubanio.com/lpic/s1092076.jpg',
         summary=u"""* 学习编程的人都知道，阅读、剖析名家代码乃是提高水平的捷径。源码之前，了无秘密。大师们的缜密思维、经验结晶、技术思路、独到风格，都原原本本体现在源码之中。
* 这本书所呈现的源码，使读者看到vector的实现、list的实现、heap的实现、deque的实现、Red Black tree的实现、hash table的实现、set/map的实现；看到各种算法（排序、查找、排列组合、数据移动与复制技术）的实现；甚至还能够看到底层的memory pool和高阶抽象的traits机制的实现。"""),
]
new_logs = [
    Log(new_users[0], new_books[0]),
]

db.session.add_all(new_users)
db.session.add_all(new_books)
# db.session.add_all(new_logs)
db.session.commit()

app_ctx.pop()
