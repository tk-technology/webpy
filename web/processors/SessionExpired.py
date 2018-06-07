#!/usr/bin/python
# -*- coding: utf-8 -*-
"""将session过期时间由根据session创建时间计算修改为根据session最近使用时间计算"""
import web
import time


def hook(handle):
    """钩子函数"""
    try:
        web.ctx.session._last_cleanup_time = time.time()
    except AttributeError:
        pass
    return handle()
