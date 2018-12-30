# encoding=utf8
"""
提供用于时间性能分析的工具
"""
import logging
from functools import wraps
from time import time

from line_profiler import LineProfiler

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
