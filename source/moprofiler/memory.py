# encoding=utf8
"""
提供用于内存性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611
from collections import defaultdict
from contextlib import contextmanager
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
    _memory_profiler = None  # type: MemoryProfiler

    @classmethod
    @contextmanager
    def _get_memory_profiler(cls, self_or_cls, **callargs):
        """
        获取内存分析器

        :param object self_or_cls: 被代理的对象 or 类
        :param dict callargs: 调用该上下文管理器时传入的所有调用参数
        :return: 返回被代理的对象 or 类
        :rtype: Iterator[object]
        """
        with super(MemoryProfilerMixin, cls)._get_profiler(
            self_or_cls, **callargs) as _self_or_cls:
            _name = callargs.get('_profiler_name')
            if not _name:  # pragma: no cover
                raise RuntimeError(u'未获取到内存分析器名称！')  # pragma: no cover
            yield base.proxy(
                _self_or_cls,
                prop_name='_memory_profiler',
                prop=_self_or_cls._MEMORY_PROFILER_POOL[_name])

    @classmethod
    def memory_profiler(cls, name):
        """
        获取指定的内存分析器

        :param str name: 指定的时间分析器名称
        :return: 时间分析器对象
        :rtype: MemoryProfiler
        :raises KeyError: 获取的键名不存在
        """
        key = base.get_default_key(cls, name)
        if key not in cls._MEMORY_PROFILER_POOL:
            raise KeyError(u'获取的键名({name})不存在！'.format(name=name))
        return cls._MEMORY_PROFILER_POOL[key]

    @staticmethod
    def profiler_manager(*dargs, **dkwargs):
        """
        返回分析器管理下的方法

        :param str name: 关键字参数，被装饰方法代理生成的 _time_profiler 所使用的名称，默认为使用被装饰方法的方法名
        :return: 装饰后的方法
        :rtype: function
        """
        invoked = bool(len(dargs) == 1 and not dkwargs and callable(dargs[0]))
        if invoked:
            func = dargs[0]  # type: types.MethodType

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
                将被封装方法所用的 self_or_cls 进行代理，并使用时间分析器对齐进行再封装
                """
                callargs = base.get_callargs(func, self_or_cls, *args, **kwargs)
                callargs.pop("cls", None)
                name = dkwargs.get('name') or func
                callargs['_profiler_name'] = base.get_default_key(self_or_cls, name)
                with self_or_cls._get_memory_profiler(self_or_cls, **callargs) as _self_or_cls:
                    profiler_wrapper = _self_or_cls._memory_profiler(func)
                    return profiler_wrapper(_self_or_cls, *args, **kwargs)
            return inner
        return wrapper if not invoked else wrapper(func)
