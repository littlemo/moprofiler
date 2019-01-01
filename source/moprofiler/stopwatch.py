# encoding=utf8
"""
提供用于计时打点的秒表工具
"""
from __future__ import absolute_import

import logging
import time
import types  # pylint: disable=W0611
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

from . import base

LOG = logging.getLogger(__name__)


def stopwatch(
        function=None, print_args=False, logger=None, fmt=None):
    """
    用于简单需求的秒表装饰器

    考虑到此装饰器主要用于装饰函数，故设计的尽量简洁，
    更复杂的功能建议使用基于 mixin 的方法装饰器

    :param types.FunctionType function: 被封装的函数，由解释器自动传入，不需关心
    :param bool print_args: 是否打印被装饰函数的参数列表，若含有较长的参数，可能造成日志过长，开启时请注意
    :param logging.Logger logger: 可传入指定的日志对象，便于统一输出样式，默认使用该模块中的全局 logger
    :param str fmt: 用于格式化输出的模板，可在了解所有内置参数变量后自行定制输出样式
    :return: 装饰后的函数
    :rtype: types.FunctionType
    """
    invoked = bool(function and callable(function))
    if invoked:
        func = function  # type: types.FunctionType
    _logger = logger or LOG
    _fmt = fmt or (
        '[性能] 统计目标: {name}, 参数列表: [{args}, {kwargs}], 耗时: {use:.4f}s'
        if print_args else '[性能] 统计目标: {name}, 耗时: {use:.4f}s')

    def wrapper(func):
        """
        装饰器封装函数

        :param types.MethodType func: 被装饰方法
        :return: 封装后的方法
        :rtype: types.MethodType
        """
        @wraps(func)
        def inner(*args, **kwargs):
            """
            在被装饰函数执行前后进行秒表计时
            """
            _begin_time = time.time()
            result = func(*args, **kwargs)
            _end_time = time.time()

            fmt_dict = {
                'name': func.__name__,
                'args': args,
                'kwargs': kwargs,
                'begin_time': _begin_time,
                'end_time': _end_time,
                'use': _end_time - _begin_time,
            }

            _logger.info(_fmt.format(**fmt_dict))
            return result
        return inner
    return wrapper if not invoked else wrapper(func)
