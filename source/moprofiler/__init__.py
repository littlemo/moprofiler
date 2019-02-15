# encoding=utf8
"""
提供针对时间、内存的分析器，以及秒表日志打点工具
"""
from .memory import MemoryProfiler, memory_profiler
from .stopwatch import StopwatchMixin, stopwatch
from .time import TimeProfiler, time_profiler

__all__ = [
    'TimeProfiler', 'MemoryProfiler',
    'StopwatchMixin', 'stopwatch',

    'time_profiler', 'memory_profiler',  # 这两个别名用于向后兼容，后续版本将删除
]
