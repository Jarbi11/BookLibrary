# -*- coding: utf-8 -*-

from app import app, db
from app.models import User, Book, Log, Role

app_ctx = app.app_context()
app_ctx.push()
db.create_all()
Role.insert_roles()

new_users = [
    User(name=u'lib_admin', email='admin@library.com', password='admin_lib', major='administrator',
         headline=u"admin", about_me=u"admin", role_id=1),

    User(name=u'test0', email='test0@test.com', password='123456', role_id=1),
    User(name=u'test1', email='test1@test.com', password='123456', role_id=2),
    User(name=u'test2', email='test2@test.com', password='123456', role_id=3),
]
new_books =[
    Book(title=u"Flask Web 开发", subtitle=u"基于Python的Web应用开发框架", author=u"Miguel Grinberg", isbn='9787115373991',
                 tags_string=u"计算机,程序设计,Web开发", image='http://img3.douban.com/lpic/s27906700.jpg',
                 summary=u"""
# 本书不仅适合初级Web开发人员学习阅读，更是Python程序员用来学习高级Web开发技术的优秀参考书。

* 学习Flask应用的基本结构，编写示例应用；
* 使用必备的组件，包括模板、数据库、Web表单和电子邮件支持；
* 使用包和模块构建可伸缩的大型应用；
* 实现用户认证、角色和个人资料；
* 在博客网站中重用模板、分页显示列表以及使用富文本；
* 使用基于Flask的REST式API，在智能手机、平板电脑和其他第三方客户端上实现可用功能；
* 学习运行单元测试以及提升性能；
* 将Web应用部署到生产服务器。
"""),

    Book(title=u"STL源码剖析", subtitle=u"庖丁解牛 恢恢乎游刃有余", author=u"侯捷", isbn='9787560926995',
                 tags_string=u"计算机,程序设计,C++", image='http://img3.doubanio.com/lpic/s1092076.jpg',
                 summary=u"""* 学习编程的人都知道，阅读、剖析名家代码乃是提高水平的捷径。源码之前，了无秘密。大师们的缜密思维、经验结晶、技术思路、独到风格，都原原本本体现在源码之中。
* 这本书所呈现的源码，使读者看到vector的实现、list的实现、heap的实现、deque的实现、Red Black tree的实现、hash table的实现、set/map的实现；看到各种算法（排序、查找、排列组合、数据移动与复制技术）的实现；甚至还能够看到底层的memory pool和高阶抽象的traits机制的实现。"""),
]
new_logs = [
    Log(new_users[0], new_books[0]),
    Log(new_users[1], new_books[1])
]


db.session.add_all([new_users,  new_books, new_logs])
db.session.commit()

app_ctx.pop()
