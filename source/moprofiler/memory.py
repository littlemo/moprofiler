# encoding=utf8
"""
提供用于内存性能分析的工具
"""
from __future__ import absolute_import

import logging
import types  # pylint: disable=W0611

from memory_profiler import LineProfiler, choose_backend, show_results

from . import base

try:
    import tracemalloc

    has_tracemalloc = True  # pragma: no cover
except ImportError:  # pragma: no cover
    has_tracemalloc = False

LOG = logging.getLogger(__name__)


class MemoryProfilerWrapper(LineProfiler):
    """
    内存分析器封装

    在原本分析器中增加统一的打印接口
    """
    def print_stats(self, stream=None, precision=1):
        """
        打印统计结果

        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param int precision: 精度
        """
        show_results(self, stream=stream, precision=precision)


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


class MemoryProfiler(base.ProfilerClassDecorator):
    """内存分析器的类装饰器"""
    profiler_factory = MemoryProfilerWrapper

    def __init__(
            self, _function=None, stream=None,
            precision=1, backend='psutil', **kwargs):
        """
        内存分析器的类装饰器

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param object stream: 输出方式，默认为 stdout ，可指定为文件
        :param int precision: 精度，默认为 1
        :param str backend: 内存监控的 backend ，默认为 'psutil'
        """
        self._backend = _process_backend(backend)
        self.profiler_kwargs = {'backend': self._backend}

        super(MemoryProfiler, self).__init__(_function=_function, **kwargs)

        # 内部属性，装饰器参数
        self._stream = stream
        self._precision = precision

    def print_stats(self):
        """打印统计结果"""
        self.profiler.print_stats(
            stream=self._stream,
            precision=self._precision)


memory_profiler = MemoryProfiler  #: 此变量是为了向后兼容旧版本的命名
