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
            self, _function=None, print_res=True,
            stream=None, output_unit=None, stripzeros=False,
            force_new_profiler=False):
        """
        时间分析器装饰器

        逐行分析被装饰函数每行的执行时间

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param bool print_res: 是否在被装饰对象退出后立刻打印分析结果，默认为 True 。
            当需要将多次调用结果聚集后输出时，可设为 False ，并通过 Mixin 中的 time_profiler 进行结果输出
        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param str output_unit: 输出单位
        :param bool stripzeros: 是否去零
        :param bool force_new_profiler: 是否强制使用新的分析器，默认为 ``否``
        :return: 装饰后的函数或方法
        :rtype: types.FunctionType or types.MethodType
        """
        # 可被外部使用的公共属性
        self.profiler = LineProfiler()

        # 内部属性
        # 被装饰函数/方法
        self._func = None
        _invoked = bool(_function and callable(_function))
        self.func = _function if _invoked \
            else None  # type: types.FunctionType or types.MethodType

        # 装饰器参数
        self._print_res = print_res
        self._stream = stream
        self._output_unit = output_unit
        self._stripzeros = stripzeros
        self._force_new_profiler = force_new_profiler

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

    def __call__(self, *args, **kwargs):
        _func = self.func
        if not self.func:
            self.func = args[0]
        return self if not _func else self._wrapper(*args, **kwargs)

    def _wrapper(self, *args, **kwargs):
        """
        将被封装方法使用 LineProfiler 进行封装
        """
        if self._force_new_profiler:
            self.profiler = LineProfiler()
        profiler_wrapper = self.profiler(self.func)
        res = profiler_wrapper(*args, **kwargs)

        if self._print_res:  # pragma: no cover
            # 此处由于 LineProfiler 的 C 库造成的 coverage 统计 Bug ，故手动配置为 no cover
            self.profiler.print_stats(
                stream=self._stream,
                output_unit=self._output_unit,
                stripzeros=self._stripzeros)

        return res  # pragma: no cover
