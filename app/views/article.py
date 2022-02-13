# -*- coding:utf-8 -*-
from fastapi import APIRouter
from datetime import datetime
from utils.decorators import login_require
from db.set_redis import r
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, Depends
from pydantic import BaseModel, constr, Field
from db.set_db import create_session
from models.articles import Article
from models.users import User
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import Optional

article_router = APIRouter()


class FormData(BaseModel):
    id: Optional[int] = None
    author: str
    content: str
    content_short: str
    display_time: str
    importance: int
    status: str
    title: str


class EditFormData(BaseModel):
    id: int = Field(..., example=1)
    title: str = Field(..., example='标题...')
    author: str
    content: str = Field(..., example='内容...')
    content_short: str
    timestamp: str
    importance: int
    status: str
    uuid: str

    class Config:
        orm_mode = True


class ListQuery(BaseModel):
    page: int
    limit: int


# 提交文章
@article_router.post('/post_article_form', summary='提交文章')
@login_require
async def post_article_form(request: Request, data: FormData, db: Session = Depends(create_session)):
    receive_form_data = jsonable_encoder(data)
    add_data = Article(author=receive_form_data['author'],
                       title=receive_form_data['title'],
                       content=receive_form_data['content'],
                       content_short=receive_form_data['content_short'],
                       display_time=receive_form_data['display_time'],
                       importance=receive_form_data['importance'],
                       status=receive_form_data['status'])
    try:
        db.add(add_data)
        db.commit()
        db.close()
        return {'code': 200, 'data': {'msg': 'add data success'}}
    except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return {'code': 500, 'data': {'msg': 'add data failed'}}


# 获取文章列表
@article_router.get('/get_article_list', summary='获取文章列表')
@login_require
async def get_article_list(request: Request, db: Session = Depends(create_session),
                           page: int = 1,
                           limit: Optional[int] = None):
    # 根据request获取user信息
    query_username = r.get(request.cookies.get('access_token'))
    roles_data = db.query(User).filter_by(deleted=0, username=query_username).first()
    print(roles_data.roles)
    total_data_query = db.query(Article).filter_by(deleted=0).all()
    total = len(total_data_query)
    article_list_query = db.query(Article).filter_by(deleted=0).limit(limit).offset((int(page) - 1) * limit)
    article_list = list()
    for index, value in enumerate(article_list_query):
        temp_dict = {'id': (index + 1) + (int(page) - 1) * limit,
                     'uuid': value.uuid,
                     'author': value.author,
                     'title': value.title,
                     'content': value.content,
                     'content_short': value.content_short,
                     'timestamp': value.display_time,
                     'importance': value.importance,
                     'status': value.status}
        article_list.append(temp_dict)
    db.close()
    return {'code': 200, 'data': {'msg': 'get article list success', 'total': total, 'article_list': article_list}}


# 获取当前文章
@article_router.get('/get_detail_data', summary='获取文章')
@login_require
async def get_detail_data(request: Request, uuid: Optional[str], db: Session = Depends(create_session)):
    article_data_query = db.query(Article).filter_by(deleted=0, uuid=uuid).first()
    db.close()
    if article_data_query:
        result_dict = {'uuid': article_data_query.uuid,
                       'author': article_data_query.author,
                       'title': article_data_query.title,
                       'content': article_data_query.content,
                       'content_short': article_data_query.content_short,
                       'timestamp': article_data_query.display_time,
                       'importance': article_data_query.importance,
                       'status': article_data_query.status,
                       }
        return {'code': 200, 'data': {'msg': 'get detail data success', 'result_dict': result_dict}}
    else:
        return {'code': 500, 'data': {'msg': 'get detail data fail'}}


# 修改文章
@article_router.post('/edit_article_data', summary='修改文章')
@login_require
async def edit_article_data(request: Request, data: EditFormData, db: Session = Depends(create_session)):
    article_query = db.query(Article).filter_by(deleted=0, uuid=data.uuid).first()
    print(article_query.title)
    if article_query:
        article_query.title = data.title
        article_query.author = data.author
        article_query.content = data.content
        article_query.content_short = data.content_short
        article_query.display_time = data.timestamp
        article_query.importance = data.importance
        article_query.status = data.status
        db.commit()
        db.refresh(article_query)
        return {'code': 200, 'data': {'msg': 'edit article success'}}
    else:
        return HTTPException(status_code=401, detail='edit article failed')


# 删除文章
@article_router.get('/delete_article_data', summary='删除文章')
@login_require
async def delete_article_data(request: Request, uuid: Optional[str], db: Session = Depends(create_session)):
    print('uuid', uuid)
    delete_data = db.query(Article).filter_by(deleted=0, uuid=uuid).first()
    try:
        delete_data.deleted = 1
        db.commit()
        db.refresh(delete_data)
        db.close()
        return {'code': 200, 'data': {'msg': 'delete article data success'}}
    except Exception as e:
        print(e)
        db.rollback()
        db.close()
        return {'code': 500, 'data': {'msg': 'delete article data failed'}}
