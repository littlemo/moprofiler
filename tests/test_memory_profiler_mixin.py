# encoding=utf8
"""
测试内存分析器 Mixin
"""
import pytest
from memory_profiler import LineProfiler

from moprofiler import MemoryProfilerMixin


class MemoryWaste(MemoryProfilerMixin):
    """
    浪费内存
    """
    @MemoryProfilerMixin.profiler_manager(name='wuwuwu')
    def list_waste(self):
        """列表"""
        a = [1] * (10 ** 5)
        b = [2] * (2 * 10 ** 5)
        del b
        return a

    @classmethod
    @MemoryProfilerMixin.profiler_manager
    def dict_waste(cls, a):
        """字典"""
        ret = {}
        for i in a:
            ret[i] = i
        return ret


class TestMemoryProfilerMixin(object):
    """测试用于装饰方法的内存分析器"""

    @staticmethod
    def test_memory_profiler_mixin():
        """测试内存分析器的 mixin"""
        mw = MemoryWaste()
        x = mw.list_waste()
        mw.dict_waste(x)
        print('内存分析器暂存池：{}'.format(MemoryProfilerMixin._MEMORY_PROFILER_POOL.keys()))
        with pytest.raises(KeyError):
            mw.memory_profiler('list_waste')
        assert isinstance(mw.memory_profiler('dict_waste'), LineProfiler)

        mw.memory_profiler('wuwuwu').print_stats()
        mw.memory_profiler('dict_waste').print_stats()


if __name__ == '__main__':
    TestMemoryProfilerMixin.test_memory_profiler_mixin()
