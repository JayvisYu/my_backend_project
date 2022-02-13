# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USERNAME = 'root'
DB_PASSWORD = '123123'
DB_HOST = '127.0.0.1'
DB_PORT = '3306'
DB_NAME = 'jarvis_management'

DB_URI = "mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8" % (DB_USERNAME, DB_PASSWORD,
                                                          DB_HOST, DB_PORT, DB_NAME)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_session():
    engine = create_engine(DB_URI, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
