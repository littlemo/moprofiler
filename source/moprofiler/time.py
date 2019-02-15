# encoding=utf8
"""
提供用于时间性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611

from line_profiler import LineProfiler

from . import base

LOG = logging.getLogger(__name__)


class TimeProfiler(base.ProfilerClassDecorator):
    """时间分析器的类装饰器"""
    profiler_factory = LineProfiler

    def __init__(
            self, _function=None, stream=None,
            output_unit=None, stripzeros=False, **kwargs):
        """
        时间分析器的类装饰器

        逐行分析被装饰函数每行的执行时间

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param str output_unit: 输出单位
        :param bool stripzeros: 是否去零
        """
        super(TimeProfiler, self).__init__(_function=_function, **kwargs)

        # 内部属性，装饰器参数
        self._stream = stream
        self._output_unit = output_unit
        self._stripzeros = stripzeros

    def print_stats(self):
        """打印统计结果"""
        self.profiler.print_stats(
            stream=self._stream,
            output_unit=self._output_unit,
            stripzeros=self._stripzeros)


time_profiler = TimeProfiler  #: 此变量是为了向后兼容旧版本的命名
