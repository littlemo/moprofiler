# encoding=utf8
"""
提供用于内存性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611
from collections import defaultdict
from functools import wraps

from memory_profiler import LineProfiler, choose_backend, show_results

from . import base

try:
    import tracemalloc

    has_tracemalloc = True  # pragma: no cover
except ImportError:  # pragma: no cover
    has_tracemalloc = False

LOG = logging.getLogger(__name__)


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

    用以提供复杂的内存分析功能，如:

    #. 针对需要多次调用的方法进行累加分析的场景
    #. 在一次代码执行流程中同时分析多个方法，并灵活控制分析结果的输出
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


def _process_backend(backend='psutil'):
    """
    处理内存分析器的后端

    :param str backend: 内存监控的 backend ，默认为 'psutil'
    :return: 处理后的后端名称
    :rtype: str
    """
    backend = choose_backend(backend)
    if backend == 'tracemalloc' and has_tracemalloc and \
       not tracemalloc.is_tracing():  # pragma: no cover
        tracemalloc.start()
    return backend


def _get_profiler(args, backend, name, func):
    """
    获取分析器

    若当前被装饰的方法未继承自 :py:class:`~moprofiler.memory.MemoryProfilerMixin` ，
    则将其当做普通函数装饰，使用指定的 ``backend`` ，进行初始化并返回

    否则，使用被装饰方法的第一个参数，并调用其
    :py:meth:`~moprofiler.memory.MemoryProfilerMixin.memory_profiler` 方法获取实例并返回

    :param list args: 被装饰方法的位置参数列表
    :param str backend: 内存分析器的处理后端
    :param str name: 关键字参数，被装饰方法所使用的内存分析器名称，默认为使用被装饰方法的方法名
    :param func: 被装饰的函数/方法
    :type func: types.FunctionType or types.MethodType
    :return: 内存分析器对象
    :rtype: MemoryProfiler
    """
    if not (args and base.is_instance_or_subclass(args[0], MemoryProfilerMixin)):
        # 若当前被装饰的方法未继承 MemoryProfilerMixin ，则将其作为普通函数装饰
        lp = MemoryProfiler(backend=backend)
    else:
        self_or_cls = args[0]  # type: MemoryProfilerMixin
        _name = name or func
        lp = self_or_cls.memory_profiler(_name, raise_except=False)
    return lp


def memory_profiler(
        _function=None, name='', print_res=True,
        stream=None, precision=1, backend='psutil'):
    """
    内存分析器装饰器

    :param _function: 被封装的对象，由解释器自动传入，不需关心
    :type _function: types.FunctionType or types.MethodType
    :param str name: 关键字参数，被装饰方法所使用的内存分析器名称，默认为使用被装饰方法的方法名
    :param bool print_res: 是否在被装饰对象退出后立刻打印分析结果，默认为 True 。
        当需要将多次调用结果聚集后输出时，可设为 False ，并通过 Mixin 中的 memory_profiler 进行结果输出
    :param object stream: 输出方式，默认为 stdout ，可指定为文件
    :param int precision: 精度，默认为 1
    :param str backend: 内存监控的 backend ，默认为 'psutil'
    :return: 装饰后的函数或方法
    :rtype: types.FunctionType or types.MethodType
    """
    invoked = bool(_function and callable(_function))
    if invoked:
        func = _function  # type: types.FunctionType or types.MethodType

    backend = _process_backend(backend)

    def wrapper(func):
        """
        装饰器封装函数
        """
        @wraps(func)
        def inner(*args, **kwargs):
            """
            将被封装方法使用 LineProfiler 进行封装
            """
            lp = _get_profiler(args, backend, name, func)

            profiler_wrapper = lp(func)
            res = profiler_wrapper(*args, **kwargs)
            if print_res:
                lp.print_stats(stream=stream, precision=precision)
            return res
        return inner
    return wrapper if not invoked else wrapper(func)
