# encoding=utf8
"""
测试用于装饰类方法的内存分析器的类装饰器
"""
import types

from memory_profiler import LineProfiler

from moprofiler import MemoryProfiler


class MemoryWaste(object):
    """
    浪费内存
    """
    @MemoryProfiler(print_res=False, fake_method=False)
    def list_waste(self):  # pylint: disable=R0201
        """列表"""
        a = [1] * (10 ** 5)
        b = [2] * (2 * 10 ** 5)
        del b
        return a

    @classmethod
    @MemoryProfiler
    def dict_waste(cls, a):
        """字典"""
        ret = {}
        for i in a:
            ret[i] = i
        return ret


class TestMemoryProfilerToMethod(object):
    """测试用于装饰方法的内存分析器"""

    @staticmethod
    def test_memory_profiler_call():
        """测试类装饰方法的内存分析器的执行"""
        mw = MemoryWaste()
        x = mw.list_waste()
        mw.dict_waste(x)

        assert mw.list_waste.__name__ == 'list_waste'
        assert mw.dict_waste.__name__ == 'dict_waste'

        assert mw.list_waste.__doc__ == '列表'
        assert mw.dict_waste.__doc__ == '字典'

        assert isinstance(mw.list_waste.profiler, LineProfiler)
        assert isinstance(mw.dict_waste.profiler, LineProfiler)

        assert isinstance(mw.list_waste, MemoryProfiler)
        assert isinstance(mw.dict_waste, types.MethodType)

        mw.list_waste.profiler.print_stats()


if __name__ == '__main__':
    TestMemoryProfilerToMethod.test_memory_profiler_call()
