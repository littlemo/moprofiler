# encoding=utf8
"""
提供用于时间性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611
from functools import update_wrapper

from line_profiler import LineProfiler

LOG = logging.getLogger(__name__)


class time_profiler(object):  # pylint: disable=R0902
    """时间分析器"""
    def __init__(
            self, _function=None, name='', print_res=True,
            stream=None, output_unit=None, stripzeros=False,
            force_new_profiler=False):
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
        :param bool force_new_profiler: 是否强制使用新的分析器，默认为 ``否``
        :return: 装饰后的函数或方法
        :rtype: types.FunctionType or types.MethodType
        """
        # 内部属性
        self._func = None
        self._profiler = LineProfiler()

        # 被装饰函数/方法
        _invoked = bool(_function and callable(_function))
        self.func = _function if _invoked \
            else None  # type: types.FunctionType or types.MethodType

        # 装饰器参数
        self.name = name
        self.print_res = print_res
        self.stream = stream
        self.output_unit = output_unit
        self.stripzeros = stripzeros
        self.force_new_profiler = force_new_profiler

    @property
    def func(self):
        """被封装函数的 getter 方法"""
        return self._func

    @func.setter
    def func(self, func):
        """被封装函数的 setter 方法"""
        if func:
            update_wrapper(self, func)
        self._func = func

    @property
    def profiler(self):
        """分析器的 getter 方法"""
        return self._profiler

    def __call__(self, *args, **kwargs):
        _func = self.func
        if not self.func:
            self.func = args[0]
        return self if not _func else self._wrapper(*args, **kwargs)

    def _wrapper(self, *args, **kwargs):
        """
        将被封装方法使用 LineProfiler 进行封装
        """
        if self.force_new_profiler:
            self._profiler = LineProfiler()
        profiler_wrapper = self._profiler(self.func)
        res = profiler_wrapper(*args, **kwargs)

        if self.print_res:  # pragma: no cover
            # 此处由于 LineProfiler 的 C 库造成的 coverage 统计 Bug ，故手动配置为 no cover
            self.profiler.print_stats(
                stream=self.stream,
                output_unit=self.output_unit,
                stripzeros=self.stripzeros)

        return res  # pragma: no cover
