# -*- coding:utf-8 -*-
import uvicorn
from routers import create_app

app = create_app()


@app.get('/')
async def index():
    return {'msg': '你已经正确开启了fastApi服务!'}


if __name__ == '__main__':
    uvicorn.run(app="main:app", host='127.0.0.1', port=7000, reload=True, debug=True)

# pip freeze > requirements.txt
