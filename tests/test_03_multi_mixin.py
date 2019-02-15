# encoding=utf8
"""
测试时间&内存分析器与秒表的共用
"""
import time

from line_profiler import LineProfiler as TimeLineProfiler
from memory_profiler import LineProfiler as MemoryLineProfiler

from moprofiler import MemoryProfiler, StopwatchMixin, TimeProfiler, stopwatch


class MultiMixin(StopwatchMixin):
    """
    混合使用两种分析器&秒表
    """
    # 不支持同时监控一个方法的时间&内存，最终会变成外层装饰器监控内层装饰器中的代码
    @MemoryProfiler
    def list_waste(self):  # pylint: disable=R0201
        """列表"""
        a = [1] * (10 ** 5)
        return a

    @classmethod
    @TimeProfiler
    def dict_waste(cls, a):
        """字典"""
        ret = {}
        for i in a:
            ret[i] = i
        return ret

    @stopwatch
    def orz_instancemethod(self, x):
        """实例方法"""
        for _i in range(x):
            self.stopwatch.dotting()
            time.sleep(0.1)
        self.stopwatch.dotting()


class TestMultiMixin(object):
    """测试用于装饰类中多个方法的多种分析器&秒表"""

    @staticmethod
    def test_multi_mixin():
        """测试多分析器&秒表共用"""
        mm = MultiMixin()
        x = mm.list_waste()
        mm.dict_waste(x)
        mm.orz_instancemethod(5)

        assert isinstance(mm.dict_waste.profiler, TimeLineProfiler)
        assert isinstance(mm.list_waste.profiler, MemoryLineProfiler)


if __name__ == '__main__':
    TestMultiMixin.test_multi_mixin()
