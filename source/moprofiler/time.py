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
    """时间分析器的类装饰器"""
    def __init__(
            self, _function=None, fake_method=False, print_res=True,
            stream=None, output_unit=None, stripzeros=False,
            force_new_profiler=False):
        """
        时间分析器装饰器

        逐行分析被装饰函数每行的执行时间

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param bool fake_method: 是否将被装饰后的类装饰器伪装成方法，默认为否。
            注意，伪装后虽然仍然可以正常调用 :py:attr:`~moprofiler.time.time_profiler.profiler`
            但将不会有语法提示，此参数仅用于装饰类方法时使用，装饰函数时无效
        :param bool print_res: 是否在被装饰对象退出后立刻打印分析结果，默认为 True 。
            当需要将多次调用结果聚集后输出时，可设为 False ，并通过 Mixin 中的 time_profiler 进行结果输出
        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param str output_unit: 输出单位
        :param bool stripzeros: 是否去零
        :param bool force_new_profiler: 是否强制使用新的分析器，默认为 ``否``
        :return: 装饰后的函数或方法
        :rtype: types.FunctionType or types.MethodType
        """
        # 被装饰函数/方法
        self._func = None
        self._instance = None
        _invoked = bool(_function and callable(_function))
        self.func = _function if _invoked \
            else None  # type: types.FunctionType or types.MethodType

        # 可被外部使用的公共属性
        self.profiler = LineProfiler()

        # 内部属性
        # 装饰器参数
        self._fake_method = fake_method
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
        if not self._fake_method and self._instance:
            args = (self._instance,) + args
        return self if not _func else self._wrapper(*args, **kwargs)

    def __get__(self, *args, **kwargs):
        self._instance = args[0]
        return types.MethodType(self, *args, **kwargs) if self._fake_method else self

    def _wrapper(self, *args, **kwargs):
        """
        将被封装方法使用 LineProfiler 进行封装
        """
        if self._force_new_profiler:
            self.profiler = LineProfiler()
        profiler_wrapper = self.profiler(self.func)
        res = profiler_wrapper(*args, **kwargs)

        # 此处由于 LineProfiler 的 C 库造成的 coverage 统计 Bug ，故手动配置为 no cover
        self._print_result()  # pragma: no cover
        return res  # pragma: no cover

    def _print_result(self):
        """打印统计结果"""
        if not self._print_res:
            return

        self.profiler.print_stats(
            stream=self._stream,
            output_unit=self._output_unit,
            stripzeros=self._stripzeros)
