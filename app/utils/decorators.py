# -*- coding:utf-8 -*-
from fastapi import HTTPException, status
from db.set_redis import r, pool
from starlette.requests import Request
from functools import wraps


def login_require(func):
    @wraps(func)
    async def inner(request: Request, *args, **kwargs):
        if r.get(request.cookies.get('access_token')):
            return await func(request, *args, **kwargs)
        else:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="token is expired, please login first",
                headers={"WWW-Authenticate": "Bearer"},
            )
            # return {'code': 514, 'data': {'msg': 'please login first'},
            #         'message': 'token is expired, please login first'}

    return inner
