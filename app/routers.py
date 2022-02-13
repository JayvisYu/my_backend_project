# -*- coding:utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from views import user_router, article_router, stock_router, option_router, digital_currency_router
from config import SESSION_COOKIE_AGE


def create_app():
    app = FastAPI()
    # 是否关闭所有接口文档
    # app = FastAPI(docs_url=None, redoc_url=None)

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 添加路由
    app.include_router(user_router, prefix='/api/user', tags=['用户模块'])
    app.include_router(article_router, prefix='/api/article', tags=['文章模块'])
    app.include_router(stock_router, prefix='/api/stock', tags=['股票模块'])
    app.include_router(option_router, prefix='/api/option', tags=['期权模块'])
    app.include_router(digital_currency_router, prefix='/api/digital_currency', tags=['数字货币模块'])
    # app.include_router(article_router, prefix='/api/future', tags=['期货模块'])

    app.add_middleware(SessionMiddleware, secret_key='Jarvis', max_age=SESSION_COOKIE_AGE)
    # app.mount('/static', StaticFiles(directory='static'), name='static')
    # app.mount('/components', StaticFiles(directory='components'), name='components')
    app.mount('/models', StaticFiles(directory='models'), name='models')
    app.mount('/data', StaticFiles(directory='data'), name='data')
    app.mount('/logs', StaticFiles(directory='logs'), name='logs')

    return app
