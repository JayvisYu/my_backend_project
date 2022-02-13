# -*- coding:utf-8 -*-
import logging


def set_log(log_path, log_name):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)

    # 多次调用会造成重复日志,每次都移除掉所有的handler,可以解决这类问题
    for i in logger.handlers:
        logger.removeHandler(i)

    # file log 写入文件配置
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(r'%s' % log_path, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
