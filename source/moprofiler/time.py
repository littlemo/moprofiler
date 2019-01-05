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


def time_profiler(
        _function=None, name='', print_res=True,
        stream=None, output_unit=None, stripzeros=False):
    """
    时间分析器装饰器

    逐行分析被装饰函数每行的执行时间

    :param _function: 被封装的对象，由解释器自动传入，不需关心
    :type _function: types.FunctionType or types.MethodType
    :param str name: 关键字参数，被装饰方法所使用的时间分析器名称，默认为使用被装饰方法的方法名
    :param bool print_res: 是否在被装饰对象退出后立刻打印分析结果，默认为 True 。
        当需要将多次调用结果聚集后输出时，可设为 False ，并通过 Mixin 中的 time_profiler 进行结果输出
    :param object stream: 输出方式，默认为 stdout ，可指定为文件
    :param str output_unit: 输出单位
    :param bool stripzeros: 是否去零
    :return: 装饰后的函数或方法
    :rtype: types.FunctionType or types.MethodType
    """
    invoked = bool(_function and callable(_function))
    if invoked:
        func = _function  # type: types.FunctionType or types.MethodType

    def wrapper(func):
        """
        装饰器封装函数
        """
        @wraps(func)
        def inner(*args, **kwargs):
            """
            将被封装方法使用 LineProfiler 进行封装
            """
            if not (args and base.is_instance_or_subclass(args[0], TimeProfilerMixin)):
                # 若当前被装饰的方法未继承 TimeProfilerMixin ，则将其作为普通函数装饰
                lp = LineProfiler()
            else:
                self_or_cls = args[0]  # type: TimeProfilerMixin
                _name = name or func
                lp = self_or_cls.time_profiler(_name, raise_except=False)

            profiler_wrapper = lp(func)
            res = profiler_wrapper(*args, **kwargs)
            if print_res:
                lp.print_stats(stream=stream, output_unit=output_unit, stripzeros=stripzeros)
            return res
        return inner
    return wrapper if not invoked else wrapper(func)
