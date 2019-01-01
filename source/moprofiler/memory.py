# encoding=utf8
"""
提供用于内存性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611
from collections import defaultdict
from functools import wraps

from memory_profiler import LineProfiler, profile, show_results

from . import base

LOG = logging.getLogger(__name__)

memory_profiler = profile  #: 仅为便于和时间分析器命名统一，主要用于简单需求的函数装饰器，函数退出时即打印结果


class MemoryProfiler(LineProfiler):
    """
    内存分析器
    """

    def print_stats(self, stream=None, precision=1):
        """
        打印统计结果

        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param int precision: 精度
        """
        show_results(self, stream=stream, precision=precision)


class MemoryProfilerMixin(base.ProfilerMixin):
    """
    内存分析器 Mixin 类

    用以提供复杂的内存分析功能，如：
    - 针对需要多次调用的方法进行累加分析的场景
    - 在一次代码执行流程中同时分析多个方法，并灵活控制分析结果的输出
    """
    # 此处若想修改 backend 可通过继承该 mixin 并修改 defaultdict 中的默认值来实现
    _MEMORY_PROFILER_POOL = defaultdict(MemoryProfiler)  #: 用来暂存内存分析器的池子

    @classmethod
    def memory_profiler(cls, name, raise_except=True):
        """
        获取指定的内存分析器

        :param str name: 指定的内存分析器名称
        :param bool raise_except: 若不存在是否抛出异常，默认为是，若为否，则会生成指定名称的分析器并返回
        :return: 内存分析器对象
        :rtype: MemoryProfiler
        :raises KeyError: 获取的键名不存在
        """
        key = base.get_default_key(cls, name)
        if raise_except and key not in cls._MEMORY_PROFILER_POOL:
            raise KeyError(u'获取的键名({name})不存在！'.format(name=name))
        return cls._MEMORY_PROFILER_POOL[key]

    @staticmethod
    def profiler_manager(function=None, name=''):
        """
        返回分析器管理下的方法

        :param function: 被封装的函数，由解释器自动传入，不需关心
        :type function: types.FunctionType or types.MethodType
        :param str name: 关键字参数，被装饰方法所使用的时间分析器名称，默认为使用被装饰方法的方法名
        :return: 装饰后的方法
        :rtype: types.MethodType
        """
        invoked = bool(function and callable(function))
        if invoked:
            func = function  # type: types.MethodType

        def wrapper(func):
            """
            装饰器封装函数

            :param types.MethodType func: 被装饰方法
            :return: 封装后的方法
            :rtype: types.MethodType
            """
            @wraps(func)
            def inner(self_or_cls, *args, **kwargs):
                """
                将被封装方法使用 LineProfiler 进行封装

                :param MemoryProfilerMixin self_or_cls:
                """
                _name = name or func
                lp = self_or_cls.memory_profiler(_name, raise_except=False)
                profiler_wrapper = lp(func)
                return profiler_wrapper(self_or_cls, *args, **kwargs)
            return inner
        return wrapper if not invoked else wrapper(func)
