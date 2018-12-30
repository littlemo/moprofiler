# encoding=utf8
"""
提供用于时间性能分析的工具
"""
import logging
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
from time import time

from line_profiler import LineProfiler
from pyaop import AOP, Proxy, Return

LOG = logging.getLogger(__name__)


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


def proxy(obj, prop, prop_name):
    """
    为 object 对象代理一个属性
    :param object obj: 被代理的对象
    :param object prop: 代理返回的属性
    :param str prop_name: 被代理的属性名
    :return: 被代理之后的对象
    :rtype: object
    """
    def common(proxy, name, value=None):
        if name == prop_name:
            Return(prop)

    return Proxy(obj, before=[
        AOP.Hook(common, ["__getattribute__", "__setattr__", "__delattr__"]),
    ])


class TimeProfilerMixin(object):
    """
    时间分析器 Mixin 类

    用以提供复杂的时间分析功能，如：
    - 针对需要多次调用的方法进行累加分析的场景
    - 在一次代码执行流程中同时分析多个方法，并灵活控制分析结果的输出
    """
    _POOL = defaultdict(LineProfiler)  #: 用来暂存分析器的池子
    time_profiler = None  # type: LineProfiler

    @classmethod
    @contextmanager
    def get_time_profiler(cls, self_or_cls, **callargs):
        """
        获取时间分析器

        :param object self_or_cls: 被代理的对象 or 类
        :param dict callargs: 调用该上下文管理器时传入的所有调用参数
        :return: 返回被代理的对象 or 类
        :rtype: Iterator[object]
        """
        with super(TimeProfilerMixin, cls).get_time_profiler(
                self_or_cls, **callargs) as self_or_cls:
            time_profiler_name = callargs.get('_time_profiler_name', 'default')
            yield proxy(
                self_or_cls,
                prop_name='time_profiler',
                prop=cls._POOL[time_profiler_name])
