# encoding=utf8
"""
提供用于时间性能分析的工具
"""
import logging
import time
import types  # pylint: disable=W0611
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

from line_profiler import LineProfiler

from . import base

LOG = logging.getLogger(__name__)


def stats_exec_time(print_args=False):
    """
    统计函数执行时间
    """
    def _decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """用于统计执行时间的封装方法"""
            _begin_time = time.time()
            result = func(*args, **kwargs)
            _end_time = time.time()

            if print_args:
                LOG.info(
                    '[性能] 统计目标: {name}, 参数列表: [{args}, '
                    '{kwargs}], 耗时: {use:.4f}s'.format(
                        name=func.__name__, args=args, kwargs=kwargs,
                        use=_end_time-_begin_time))
            else:
                LOG.info(
                    '[性能] 统计目标: {name}, 耗时: {use:.4f}s'.format(
                        name=func.__name__, use=_end_time-_begin_time))
            return result
        return wrapper
    return _decorate


def time_profiler(func):
    """
    用于单独的函数，逐行分析被装饰函数每行的执行时间

    此装饰器将在被装饰函数执行结束后将统计结果打印到 stdout 。
    考虑到此装饰器主要用于装饰函数，故设计的尽量简洁，
    更复杂的功能建议使用基于 mixin 的方法装饰器
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
    _PROFILER_POOL = defaultdict(LineProfiler)  #: 用来暂存时间分析器的池子
    _time_profiler = None  # type: LineProfiler

    @classmethod
    @contextmanager
    def _get_profiler(cls, self_or_cls, **callargs):
        """
        获取时间分析器

        :param object self_or_cls: 被代理的对象 or 类
        :param dict callargs: 调用该上下文管理器时传入的所有调用参数
        :return: 返回被代理的对象 or 类
        :rtype: Iterator[object]
        """
        with super(TimeProfilerMixin, cls)._get_profiler(
            self_or_cls, **callargs) as _self_or_cls:
            _name = callargs.get('_profiler_name')
            if not _name:
                raise RuntimeError('未获取到时间分析器名称！')
            yield base.proxy(
                _self_or_cls,
                prop_name='_time_profiler',
                prop=cls._PROFILER_POOL[_name])

    @classmethod
    def time_profiler(cls, name):
        """
        获取指定的时间分析器

        :param str name: 指定的时间分析器名称
        :return: 时间分析器对象
        :rtype: LineProfiler
        :raises KeyError: 获取的键名不存在
        """
        key = base.get_default_key(cls, name)
        if key not in cls._PROFILER_POOL:
            raise KeyError('获取的键名({name})不存在！'.format(name=name))
        return cls._PROFILER_POOL[key]

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
                with self_or_cls._get_profiler(self_or_cls, **callargs) as _self_or_cls:
                    profiler_wrapper = _self_or_cls._time_profiler(func)
                    return profiler_wrapper(_self_or_cls, *args, **kwargs)
            return inner
        return wrapper if not invoked else wrapper(func)
