# encoding=utf8
"""
提供用于时间性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611
from collections import defaultdict
from functools import wraps

from line_profiler import LineProfiler

from . import base

LOG = logging.getLogger(__name__)


def time_profiler(func):
    """
    用于简单需求的函数装饰器

    该装饰器同时支持装饰函数和方法

    逐行分析被装饰函数每行的执行时间，
    此装饰器将在被装饰函数执行结束后将统计结果打印到 stdout 。
    考虑到此装饰器主要用于装饰函数，故设计的尽量简洁，
    更复杂的功能建议使用基于 mixin 的方法装饰器

    :param func: 被装饰的函数或方法
    :type func: types.FunctionType or types.MethodType
    :return: 封装后的方法
    :rtype: types.FunctionType or types.MethodType
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """用于统计每行执行时间的封装方法"""
        lp = LineProfiler()
        lp_wrap = lp(func)
        func_return = lp_wrap(*args, **kwargs)
        lp.print_stats()
        return func_return
    return wrapper


class TimeProfilerMixin(base.ProfilerMixin):
    """
    时间分析器 Mixin 类

    用以提供复杂的时间分析功能，如：
    - 针对需要多次调用的方法进行累加分析的场景
    - 在一次代码执行流程中同时分析多个方法，并灵活控制分析结果的输出
    """
    _TIME_PROFILER_POOL = defaultdict(LineProfiler)  #: 用来暂存时间分析器的池子

    @classmethod
    def time_profiler(cls, name, raise_except=True):
        """
        获取指定的时间分析器

        :param str name: 指定的时间分析器名称
        :return: 时间分析器对象
        :param bool raise_except: 若不存在是否抛出异常，默认为是，若为否，则会生成指定名称的分析器并返回
        :rtype: LineProfiler
        :raises KeyError: 获取的键名不存在
        """
        key = base.get_default_key(cls, name)
        if raise_except and key not in cls._TIME_PROFILER_POOL:
            raise KeyError(u'获取的键名({name})不存在！'.format(name=name))
        return cls._TIME_PROFILER_POOL[key]

    @staticmethod
    def profiler_manager(method=None, name=''):
        """
        返回分析器管理下的方法

        :param method: 被封装的方法，由解释器自动传入，不需关心
        :type method: types.MethodType
        :param str name: 关键字参数，被装饰方法所使用的时间分析器名称，默认为使用被装饰方法的方法名
        :return: 装饰后的方法
        :rtype: types.MethodType
        """
        invoked = bool(method and callable(method))
        if invoked:
            meth = method  # type: types.MethodType

        def wrapper(meth):
            """
            装饰器封装函数

            :param types.MethodType meth: 被装饰方法
            :return: 封装后的方法
            :rtype: types.MethodType
            """
            @wraps(meth)
            def inner(self_or_cls, *args, **kwargs):
                """
                将被封装方法使用 LineProfiler 进行封装

                :param TimeProfilerMixin self_or_cls: 时间分析器 Mixin
                """
                _name = name or meth
                lp = self_or_cls.time_profiler(_name, raise_except=False)
                profiler_wrapper = lp(meth)
                return profiler_wrapper(self_or_cls, *args, **kwargs)
            return inner
        return wrapper if not invoked else wrapper(meth)
