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

__time_profiler_pool = defaultdict(LineProfiler)  #: 用来存储时间分析器的池子


def _make_time_profiler_getter(self_or_cls=None):
    """
    生成时间分析器获取器

    :param TimeProfilerMixin self_or_cls: 时间分析器 Mixin 实例或类
    """
    def _profiler_getter(name, raise_except=True):
        """
        闭包方法，获取时间分析器

        :param str name: 指定的时间分析器名称
        :param bool raise_except: 若不存在是否抛出异常，默认为是，若为否，则会生成指定名称的分析器并返回
        :return: 时间分析器对象
        :rtype: LineProfiler
        :raises KeyError: 获取的键名不存在
        """
        if self_or_cls:
            name = base.get_default_key(self_or_cls, name)
        if name not in __time_profiler_pool:
            if raise_except:
                raise KeyError(u'获取的键名({name})不存在！'.format(name=name))
            LOG.info(u'创建新的时间分析器: {}'.format(name))
        return __time_profiler_pool[name]
    return _profiler_getter


time_profiler_getter = _make_time_profiler_getter()  #: 用于存储装饰函数、静态方法时创建的时间分析器


class TimeProfilerMixin(base.ProfilerMixin):
    """
    时间分析器 Mixin 类

    用以提供复杂的时间分析功能，如:

    #. 针对需要多次调用的方法进行累加分析的场景
    #. 在一次代码执行流程中同时分析多个方法，并灵活控制分析结果的输出
    """

    @classmethod
    def time_profiler(cls, name, raise_except=True):
        """
        获取指定的时间分析器

        :param str name: 指定的时间分析器名称
        :param bool raise_except: 若不存在是否抛出异常，默认为是，若为否，则会生成指定名称的分析器并返回
        :return: 时间分析器对象
        :rtype: LineProfiler
        :raises KeyError: 获取的键名不存在
        """
        return _make_time_profiler_getter(cls)(name, raise_except=raise_except)


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
            _name = name or func.__name__
            if not (args and base.is_instance_or_subclass(args[0], TimeProfilerMixin)):
                # 若当前被装饰的方法未继承 TimeProfilerMixin ，则将其作为普通函数装饰
                lp = time_profiler_getter(_name, raise_except=False)
            else:
                self_or_cls = args[0]  # type: TimeProfilerMixin
                lp = self_or_cls.time_profiler(_name, raise_except=False)

            profiler_wrapper = lp(func)
            res = profiler_wrapper(*args, **kwargs)
            if print_res:  # pragma: no cover
                # 此处由于 LineProfiler 的 C 库造成的 coverage 统计 Bug ，故手动配置为 no cover
                lp.print_stats(
                    stream=stream,
                    output_unit=output_unit,
                    stripzeros=stripzeros)
            return res  # pragma: no cover
        return inner
    return wrapper if not invoked else wrapper(func)
