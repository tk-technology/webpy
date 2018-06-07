#!/usr/bin/python
# -*- coding: utf-8 -*-
"""判断web请求的path是否存在，将path不存在的web请求重定向至登录页"""

import web
from common.config import DatabaseConfig
from common.alchemy_database import USMApiAlchemy


########################################################################################################################
# 根据usm_api表生成全部有效path
########################################################################################################################
class WebAppAlias(object):
    def __init__(self, rid, alias, pid=None):
        """
        :param rid: Web应用别名数据记录id
        :param alias: Web应用别名
        :param pid: 父应用别名数据记录id
        """

        self.rid = rid
        self.alias = alias
        self.pid = pid
        self.childAlias = list()  # 子应用WebAppAlias类的列表

    def append(self, subPath):
        """添加子应用的WebAppAlias类实例"""

        self.childAlias.append(subPath)

root = WebAppAlias(rid=0, alias='')  # 根节点


def _getValidPath():
    """返回Web项目中全部有效path"""

    def generatePath(webAppAlias):
        """递归生成path"""

        if webAppAlias.childAlias:
            return [webAppAlias.alias + suffix for child in webAppAlias.childAlias for suffix in generatePath(child)]
        else:
            return [webAppAlias.alias]

    # 根据数据库记录，生成全部WebAppAlias实例
    records = DatabaseConfig.DB_READ_SESSION().query(USMApiAlchemy.USMApi).all()
    allAlias = [WebAppAlias(r.id, r.url, r.pid) for r in records]
    relation = {alias.rid: alias for alias in allAlias}
    relation[0] = root
    for alias in allAlias:
        relation[alias.pid].append(alias)

    # 递归生成path并返回
    return generatePath(root)

validPaths = _getValidPath()


########################################################################################################################
# hook
########################################################################################################################
def hook(handler):
    """身份验证钩子函数"""

    # 次级应用无需进行path有效性判断
    if '_oldctx' in web.ctx:
        return handler()

    # 判断访问路径是否有效，无效则重定向至登录页
    if web.ctx.path not in validPaths:
        raise web.webapi.SeeOther(url='/static/html/login.html')

    return handler()


if __name__ == '__main__':
    pass
