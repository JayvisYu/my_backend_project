# -*- coding:utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from utils.security import LoginUserInfo, Token
from utils.security import create_access_token, jwt_authenticate_user
from utils.decorators import login_require
from sqlalchemy.orm import Session
from db.set_db import create_session
from db.set_redis import r, pool
from models.users import User
from starlette.requests import Request
from typing import Optional, List
from pydantic import BaseModel, constr, Field
from datetime import timedelta
import config
import uuid

user_router = APIRouter()


class AddUserInfo(BaseModel):
    username: str = Field(..., example="ZhaoSi")
    password: constr(min_length=6)
    email: str = ''
    roles: str = Field(..., example="admin")
    introduction: str = None
    avatar: str = None


class EditUserInfo(BaseModel):
    uuid: str = None
    username: str = Field(..., example="ZhaoSi")
    password: constr(min_length=6)
    email: str = ''
    roles: str = Field(..., example="admin")
    introduction: str = None
    avatar: str = None

    class Config:
        orm_mode = True


# 用户登录
@user_router.post('/login', summary='用户登录')
async def login(user_info: LoginUserInfo):
    user = jwt_authenticate_user(User, user_info.username, user_info.password)
    if user:
        # 如果用户正确通过 则生成token
        # 设置过期时间
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': user_info.username}, expires_delta=access_token_expires
        )
        user_name = user.get('username')
        # redis存储用户的tokern信息
        r.set(access_token, user_name, ex=config.REDIS_EXPIRE_TIME)
        return {'code': 200, 'data': {'access_token': access_token, 'token_type': 'bearer'}}
    else:
        raise HTTPException(
            status_code=401,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )


# token验证
@user_router.get('/info', summary='获取用户信息')
@login_require
async def info(request: Request, token: Optional[str]):
    print('token', token)
    # 判断token是否过期
    if r.get(token):
        username = r.get(token)
        session = create_session()
        user_query = session.query(User).filter_by(username=username).first()
        user_dict = {'username': user_query.username,
                     'email': user_query.email,
                     'roles': [user_query.roles],
                     'introduction': user_query.introduction,
                     'avatar': user_query.avatar}
        session.close()

        return {'code': 200, 'data': user_dict}
    else:
        return {'code': 514, 'data': {'msg': 'token is expired'}}


# 用户登出
@user_router.post('/logout', summary='用户登出')
@login_require
async def logout(request: Request):
    token = request.cookies.get('access_token', '')
    if token:
        try:
            # 销毁token并退出
            r.delete(token)
            return {'code': 200, 'data': {'msg': 'Logout success'}}
        except Exception as e:
            print(e)
            return {'code': 402, 'data': {'msg': 'Logout fail'}}
    else:
        return {'code': 508, 'data': {'msg': 'Illegal token'}}


# 获取用户列表
@user_router.get('/get_search_user', summary='获取用户列表')
@login_require
async def get_search_user(request: Request, name: Optional[str]):
    session = create_session()
    user_query = session.query(User).filter_by(name=name).all()
    user_list = []
    for item in user_query:
        temp_user = dict()
        temp_user['name'] = item.name
        user_list.append(item)
    session.close()
    return {'code': 200, 'data': {'items': user_list, 'msg': 'success'}}


# 获取用户角色列表
@user_router.get('/fetch_roles_list', summary='获取用户角色列表')
@login_require
async def fetch_roles_list(request: Request, db: Session = Depends(create_session),
                           page: int = 1,
                           limit: Optional[int] = None):
    user_query = db.query(User).filter_by(deleted=0).all()
    total = len(user_query)
    user_table = list()
    pagination_data = db.query(User).filter_by(deleted=0).limit(limit).offset((int(page) - 1) * limit)
    for item in pagination_data:
        temp_user = {
            'uuid': item.uuid,
            'username': item.username,
            'email': item.email,
            'roles': item.roles,
            'introduction': item.introduction,
            'avatar': item.avatar}
        user_table.append(temp_user)
    db.close()
    return {'code': 200, 'data': {'user_table': user_table, 'total': total}}


# 添加用户
@user_router.post('/add_user_data', summary='添加用户')
@login_require
async def add_user_data(request: Request, user_info: AddUserInfo, db: Session = Depends(create_session)):
    username = user_info.username
    print('username', username)
    user_query = db.query(User).filter_by(deleted=0, username=username).first()
    if not user_query:
        add_data = User(**user_info.dict())
        try:
            db.add(add_data)
            db.commit()
            db.refresh(add_data)
        except Exception as e:
            print(e)
            db.rollback()
            raise HTTPException(status_code=401, detail="add user failed")
        finally:
            db.close()
        return {'code': 200, 'data': {'msg': 'success'}}
    else:
        db.close()
        raise HTTPException(status_code=401, detail="username is already exist")


# 修改用户
@user_router.post('/edit_user_data', summary='修改用户')
@login_require
async def edit_user_data(request: Request, user_info: EditUserInfo, db: Session = Depends(create_session)):
    user_query = db.query(User).filter_by(deleted=0, uuid=user_info.uuid).first()
    print(user_info.username)
    if user_query:
        user_query.username = user_info.username
        user_query.password = user_info.password
        user_query.roles = user_info.roles
        user_query.email = user_info.email
        user_query.introduction = user_info.introduction
        user_query.avatar = user_info.avatar
        db.commit()
        db.refresh(user_query)
        return {'code': 200, 'data': {'msg': 'success'}}
    else:
        return HTTPException(status_code=401, detail='edit user failed')


# 删除用户
@user_router.get('/delete_user_data', summary='删除用户')
@login_require
async def delete_user_data(request: Request, uuid: str = Query(...), db: Session = Depends(create_session)):
    print('uuid', uuid)
    user_query = db.query(User).filter_by(deleted=0, uuid=uuid).first()
    if user_query:
        user_query.deleted = 1
        db.commit()
        db.refresh(user_query)
        db.close()
        return {'code': 200, 'data': {'msg': 'success'}}
    else:
        raise HTTPException(status_code=401, detail='no user found!')

# 测试
# @user_router.get('/get_form')
# @login_require
# async def get_form(request: Request):
#     return {'code': 200, 'data': {'msg': 'form_get_success'}}
