# encoding=utf8
"""
测试时间&内存分析器 Mixin 的共用
"""
import pytest
from line_profiler import LineProfiler as TimeLineProfiler

from moprofiler import MemoryProfilerMixin, TimeProfilerMixin


class TimeAndMemoryWaste(MemoryProfilerMixin, TimeProfilerMixin):
    """
    浪费时间&内存
    """
    # 不支持同时监控一个方法的时间&内存，最终会变成外层装饰器监控内层装饰器中的代码
    @MemoryProfilerMixin.profiler_manager(name='wuwuwu')
    def list_waste(self):  # pylint: disable=R0201
        """列表"""
        a = [1] * (10 ** 5)
        return a

    @classmethod
    @TimeProfilerMixin.profiler_manager
    def dict_waste(cls, a):
        """字典"""
        ret = {}
        for i in a:
            ret[i] = i
        return ret


class TestTimeAndMemoryProfilerMixin(object):
    """测试用于装饰方法的内存分析器"""

    @staticmethod
    def test_time_and_memory_profiler_mixin():
        """测试内存分析器的 mixin"""
        tmw = TimeAndMemoryWaste()
        x = tmw.list_waste()
        tmw.dict_waste(x)
        print('\n时间分析器暂存池：{}'.format(TimeProfilerMixin._TIME_PROFILER_POOL.keys()))
        print('内存分析器暂存池：{}'.format(MemoryProfilerMixin._MEMORY_PROFILER_POOL.keys()))
        with pytest.raises(KeyError):
            tmw.memory_profiler('list_waste')
        assert isinstance(tmw.time_profiler('dict_waste'), TimeLineProfiler)

        tmw.memory_profiler('wuwuwu').print_stats()
        tmw.time_profiler('dict_waste').print_stats()


if __name__ == '__main__':
    TestTimeAndMemoryProfilerMixin.test_time_and_memory_profiler_mixin()
