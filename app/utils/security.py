# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from typing import Any, Union, Optional
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, constr
from passlib.context import CryptContext
from db.set_db import create_session
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import jwt
from fastapi import Header
import time
import hashlib
import hmac


class LoginUserInfo(BaseModel):
    username: str
    password: constr(min_length=6)



class Token(BaseModel):
    token: str
    token_type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """对密码进行校验"""
    return pwd_context.verify(plain_password, hashed_password)


# 生成加密密码
def get_password_hash(password: str) -> str:
    """
    加密明文
    :param password: 明文密码
    :return:
    """
    return pwd_context.hash(password)


# 查询用户返回用户密码(加密过的)
def jwt_get_user(db, username: str):
    session = create_session()
    user_query = session.query(db).filter_by(username=username).first()
    session.close()

    if user_query:
        user_dict = {'username': user_query.username,
                     'password': user_query.password,
                     'email': user_query.email,
                     'roles': user_query.roles,
                     'introduction': user_query.introduction,
                     'avatar': user_query.avatar
                     }

        return user_dict


# 验证用户
def jwt_authenticate_user(db, username: str, password: str):
    user = jwt_get_user(db=db, username=username)
    print('user', user)
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user['password']):
        return False
    return user


# 创建token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 验证token
def get_sign(ak: str, nonce: str, ts: str, sk: str) -> str:
    """
    生成签名
    ak:也可以使用各自的id
    nonce:随机值
    ts:10位时间戳
    sk:secret加密用
    """
    # self.nonce = str(uuid.uuid1()).replace("-", "")
    # nonce = str(uuid.uuid1()).replace("-", "")
    a = [ak, nonce, ts]
    a.sort()
    # a = [self.ak, 'ZPMxNpPhmrPzQj27AGKijM3FmEcHW4BY', '1550032562']

    join_str = "".join(a)
    # print(join_str)
    return hmac.new(sk.encode(), join_str.encode(), hashlib.sha256).hexdigest()


async def token_is_true(server_id: str = Header(..., ), nonce: str = Header(..., ), timestamp: str = Header(..., ),
                        token: str = Header(..., description="token验证")):
    """签名验证，全局使用,超过60秒或者验证失败就会报错"""
    if time.time() - int(timestamp) > 60 or token == get_sign(server_id, nonce, timestamp, SECRET_KEY):
        raise HTTPException(
            status_code=401,
            detail="token is fail",
            headers={"X-Error": "There goes error"},
        )
    else:
        return {"msg": server_id}  # 可以自定义返回值，比如user或者其他的数据
