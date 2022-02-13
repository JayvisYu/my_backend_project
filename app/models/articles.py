# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from db.set_db import create_engine, create_session, DB_URI
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
import uuid

Base = declarative_base()


def init_article_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.create_all(engine)


def drop_article_db():
    engine = create_engine(DB_URI, echo=False)
    Base.metadata.drop_all(engine)


class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(64))  # 作者
    title = Column(String(64))  # 标题
    content = Column(LONGTEXT)  # 文章内容
    content_short = Column(String(128))  # 文章摘要
    # source_uri = Column(String(128))  # 文章外联
    # image_uri = Column(String(128))  # 文章图片
    display_time = Column(DateTime)  # 发表时间
    importance = Column(Integer)  # 重要性
    status = Column(String(16))  # 文章状态
    uuid = Column(String(64))
    article_join_time = Column(DateTime, default=datetime.now())  # 保存时间
    deleted = Column(Integer, default=0)

    def __init__(self, author, title, content, content_short, display_time, importance, status):
        self.author = author
        self.title = title
        self.content = content
        self.content_short = content_short
        self.display_time = display_time
        self.importance = importance
        self.status = status
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.title))


if __name__ == '__main__':
    # 删除数据库
    drop_article_db()
    # 初始化数据库
    init_article_db()

    # 添加用户
    # add_article_data = User(username='editor', password='123123', roles=['editor'],
    #                        introduction='I am an editor',
    #                        avatar='https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
    #                        name='Normal Editor')
    # session = create_session()
    # session.add(add_article_data)
    # session.commit()
    # session.close()
