# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from db.set_db import create_engine, create_session, DB_URI
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
from utils.security import get_password_hash
import uuid

Base = declarative_base()


def init_user_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.create_all(engine)


def drop_user_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.drop_all(engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True)
    _password = Column(String(200), nullable=False)
    email = Column(String(64))
    roles = Column(String(64), default='editor')
    introduction = Column(String(200))
    avatar = Column(String(200))
    uuid = Column(String(64))
    user_join_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)

    def __init__(self, username, password, email, roles, introduction, avatar):
        self.username = username
        self.password = password
        self.email = email
        self.roles = roles
        self.introduction = introduction
        self.avatar = avatar
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.username))

    __mapper_args__ = {"order_by": user_join_time}  # 默认是正序, 倒序加上.desc()方法

    def __repr__(self):
        return f'该用户为{self.username}角色为{self.roles}'

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = get_password_hash(raw_password)


# 密码: 对外的字段名叫做password
# 密码: 对内的字段名叫做_password


if __name__ == '__main__':
    # 删除数据库
    drop_user_db()
    # 初始化数据库
    init_user_db()

    # 添加用户
    add_visit_user = User(username='aaa', password='123123', roles='visitor',
                          email='3213145dsa@qq.com',
                          introduction='I am a visitor',
                          avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                          )
    add_editor_user = User(username='bbb', password='123123',
                           email='982020991@qq.com', roles='editor',
                           introduction='I am an editor',
                           avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif')
    add_admin_user = User(username='ccc', password='123123',
                          email='215198532@qq.com', roles='admin',
                          introduction='I am a admin',
                          avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif')
    add_super_admin_user = User(username='ddd', password='123123', roles='super_admin',
                                email='15824456718@163.com',
                                introduction='I am a super administrator',
                                avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif')
    session = create_session()
    session.add(add_visit_user)
    session.add(add_editor_user)
    session.add(add_admin_user)
    session.add(add_super_admin_user)
    session.commit()
    session.close()
