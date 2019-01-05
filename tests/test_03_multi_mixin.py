# encoding=utf8
"""
测试时间&内存分析器 Mixin 的共用
"""
import time

import pytest
from line_profiler import LineProfiler as TimeLineProfiler

from moprofiler import (MemoryProfilerMixin, StopwatchMixin, TimeProfilerMixin,
                        memory_profiler, stopwatch, time_profiler)


class MultiMixin(MemoryProfilerMixin, TimeProfilerMixin, StopwatchMixin):
    """
    混合 Mixin
    """
    # 不支持同时监控一个方法的时间&内存，最终会变成外层装饰器监控内层装饰器中的代码
    @memory_profiler(name='wuwuwu')
    def list_waste(self):  # pylint: disable=R0201
        """列表"""
        a = [1] * (10 ** 5)
        return a

    @classmethod
    @time_profiler
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
    """测试用于装饰方法的内存分析器"""

    @staticmethod
    def test_multi_mixin():
        """测试内存分析器的 mixin"""
        mm = MultiMixin()
        x = mm.list_waste()
        mm.dict_waste(x)
        mm.orz_instancemethod(5)
        print('\n时间分析器暂存池：{}'.format(TimeProfilerMixin._TIME_PROFILER_POOL.keys()))
        print('内存分析器暂存池：{}'.format(MemoryProfilerMixin._MEMORY_PROFILER_POOL.keys()))
        with pytest.raises(KeyError):
            mm.memory_profiler('list_waste')
        assert isinstance(mm.time_profiler('dict_waste'), TimeLineProfiler)

        mm.memory_profiler('wuwuwu').print_stats()
        mm.time_profiler('dict_waste').print_stats()


if __name__ == '__main__':
    TestTimeAndMemoryProfilerMixin.test_time_and_memory_profiler_mixin()
