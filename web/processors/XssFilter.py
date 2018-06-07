#!/usr/bin/python
# -*- coding: utf-8 -*-
"""XSS过滤器"""

# 字符转换关系
escape = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    '\'': '&apos;',
    '\"': '&quot;',
}


def filterStr(s):
    """对字符串进行XSS过滤"""

    # 类型判断
    if not isinstance(s, basestring):
        raise TypeError

    # 空字符串直接返回
    if not s:
        return s

    # 过滤非空字符串
    conj = '' if isinstance(s, str) else u''
    for k, v in escape.items():
        s = map(lambda c: v if c == k else c, s)
    return conj.join(s)


def xssFilter(data):
    """递归对业务数据进行XSS过滤"""

    dataType = type(data)
    if data is None:
        pass
    elif issubclass(dataType, basestring):
        data = filterStr(data)
    elif issubclass(dataType, dict):
        data = {xssFilter(k): xssFilter(v) for k, v in data.items()}
    elif reduce(lambda x, c: x or issubclass(dataType, c), (list, tuple), False):
        data = [xssFilter(item) for item in data]
    elif reduce(lambda x, c: x or issubclass(dataType, c), (int, long, float, bool), False):
        pass
    else:
        print data
        raise TypeError

    return data


def hook(handler):
    """钩子函数"""

    result = handler()
    result = xssFilter(result)
    return result


if __name__ == '__main__':
    test = {
        1: ['a', None],
        '\'\"<>&': (1.1, {}),
        'abc': True
    }
    print xssFilter(test)
