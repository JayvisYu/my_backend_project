# -*- coding:utf-8 -*-
import redis
import config

REDIS_HOST = 'localohost'
REDIS_PORT = 6379
REDIS_PASSWD = 'abc123456'

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
    # password='abc123456',
    # db=3
)

pool = redis.ConnectionPool(
    host='localhost',
    port='6379',
    # password='abc123456',
    # db=3,
    decode_responses=True,
    max_connections=20
)


# class RedisDb():
#     def __init__(self, host, port):
#         # 建立数据库连接
#         self.r = redis.Redis(
#             host=host,
#             port=port,
#             # password=passwd,
#             decode_responses=True  # get() 得到字符串类型的数据
#         )
#
#     def handle_redis_token(self, key, value=None):
#         if value:  # 如果value非空，那么就设置key和value，EXPIRE_TIME为过期时间
#             self.r.set(key, value, ex=config.REDIS_EXPIRE_TIME)
#         else:  # 如果value为空，那么直接通过key从redis中取值
#             redis_token = self.r.get(key)
#             return redis_token
#
#
# redis_db = RedisDb(REDIS_HOST, REDIS_PORT)
