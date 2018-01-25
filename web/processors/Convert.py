#!/usr/bin/python
# -*- coding: utf-8 -*-
"""封装业务处理类的结果和异常，使USM后台接口可以更简便、统一地向前端返回数据"""

import web
import json
import logging
import traceback


class JsonEncodeError(web.HTTPError):
    """JSON序列化错误"""
    message = '510 json encode error'

    def __init__(self, message=None):
        super(JsonEncodeError, self).__init__('510 Json Encode Error', data=message or self.message)


def hook(handler):
    """
    钩子函数，封装业务处理结果、封装身份验证异常、封装业务处理异常
    自定义异常代码为：
        420: 未通过身份验证（session方式）
        421: 未通过身份验证（sign方式）
        510：JSON序列化错误
    """

    # 执行业务处理逻辑，捕获身份验证异常和业务处理异常
    try:
        result = handler()
    except (KeyboardInterrupt, SystemExit):
        raise
    except web.HTTPError:
        tb = traceback.format_exc()
        logging.warn('%s. Request: %s%s\n%s', web.ctx.status, web.ctx.home, web.ctx.fullpath, tb)
        raise

    # 封装返回数据，捕获JSON序列化异常
    try:
        result = json.dumps(result)
        logging.info('%s. Request: %s%s', web.ctx.status, web.ctx.home, web.ctx.fullpath)
        return result
    except TypeError:
        tb = traceback.format_exc()
        logging.error('%s. Request: %s%s\n%s', web.ctx.status, web.ctx.home, web.ctx.fullpath, tb)
        raise JsonEncodeError()
