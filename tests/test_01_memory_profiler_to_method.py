# encoding=utf8
"""
测试内存分析器 Mixin
"""
import pytest
from memory_profiler import LineProfiler

from moprofiler import MemoryProfilerMixin, memory, memory_profiler


class MemoryWaste(MemoryProfilerMixin):
    """
    浪费内存
    """
    @memory_profiler(name='wuwuwu', print_res=False)
    def list_waste(self):  # pylint: disable=R0201
        """列表"""
        a = [1] * (10 ** 5)
        b = [2] * (2 * 10 ** 5)
        del b
        return a

    @classmethod
    @memory_profiler
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
        print('内存分析器暂存池：{}'.format(getattr(memory, '__memory_profiler_pool').keys()))
        with pytest.raises(KeyError):
            mw.memory_profiler('list_waste')
        assert isinstance(mw.memory_profiler('dict_waste'), LineProfiler)

        mw.memory_profiler('wuwuwu').print_stats()


if __name__ == '__main__':
    TestMemoryProfilerMixin.test_memory_profiler_mixin()
