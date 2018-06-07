#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
身份验证，允许三种验证方式：IP白名单、签名、cookie-session。

IP白名单不推荐使用；
具备appId、timestamp和sign三个参数的请求使用签名进行身份验证，建议服务器间访问使用；
其他请求通过账号密码登录后，使用session维护登录状态，并基于session进行身份验证，建议PC访问使用，未登录时访问除/login以外
的接口时将重定向至登录静态页面。
"""

import web
import time
import hashlib

loginPath = '/login'
indexPath = '/static/html/login.html'


def _md5(s):
    """返回md5摘要"""

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def _validSign():
    """
    判断签名合法性。判断规则：有序连接salt和URL参数（URL中的sign参数除外；均转换为小写；按key递增排列；使用空字符串连接），
    获取的md5摘要等于sign参数的值则身份验证通过。举例说明如何构造通过签名进行身份验证的URL：
        原始接口URL为：http://domain:port/path?b=1
        假设appId=test且timestamp=1516004182
        sign=md5('appIdtestb1saltd74e53a397924be06351f06388e7067dtimestamp1516004182')
        最终URL为：http://domain:port/path?b=1&appId=test&timestamp=1516004182&sign=92abce8180f7e58303fd43be363a40e3
    """

    params = dict(salt='d74e53a397924be06351f06388e7067d')
    params.update(web.input())
    newParams = sorted([k + v for k, v in params.items() if k != 'sign'])
    return float(params['timestamp']) > time.time() - 60 * 10 and params['sign'] == _md5(''.join(newParams).lower())


class NoLogin(web.HTTPError):
    """未登录"""
    message = '420 no login'

    def __init__(self, message=None):
        super(NoLogin, self).__init__('420 No Login', data=message or self.message)


class SignError(web.HTTPError):
    """未通过身份验证（sign方式）"""
    message = '421 sign error'

    def __init__(self, message=None):
        super(SignError, self).__init__('421 Sign Error', data=message or self.message)


def hook(handler):
    """身份验证钩子函数"""

    # 次级应用无需进行身份验证
    if '_oldctx' in web.ctx:
        return handler()

    # 依次尝试白名单、签名、session进行身份验证
    params = web.input()
    if web.ctx.ip in []:
        pass
    elif 'appId' in params and 'timestamp' in params and 'sign' in params:
        if not _validSign():
            raise SignError()
    else:
        if web.ctx.session.login is False and web.ctx.path != loginPath:
            raise NoLogin()

    return handler()
