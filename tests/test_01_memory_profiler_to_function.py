# encoding=utf8
"""
测试用于装饰函数的内存分析器的类装饰器
"""
import gc

from memory_profiler import LineProfiler

from moprofiler import MemoryProfiler


@MemoryProfiler
def calc_sum():
    """求和计算"""
    _sum = 0
    for _item in range(10000):
        _sum += 1
    return _sum


@MemoryProfiler(print_res=False, fake_method=False)
def calc_sum_2(x=10000):
    """求和计算"""
    _sum = 0
    for _item in range(x):
        _sum += 1
    return _sum


class TestMemoryProfilerToFunction(object):
    """测试用于装饰函数的内存分析器类装饰器"""

    @staticmethod
    def test_memory_profiler_call():
        """测试内存分析器装饰器"""
        # 此处由于内存计算处理的加载机制问题，在单测中无法正常统计到
        assert isinstance(calc_sum.profiler, LineProfiler)
        assert isinstance(calc_sum_2.profiler, LineProfiler)

        print('求和结果: {}'.format(calc_sum()))
        gc.collect()
        calc_sum_2(10000)

        assert isinstance(calc_sum.profiler, LineProfiler)
        assert isinstance(calc_sum_2.profiler, LineProfiler)
        assert calc_sum.profiler is not calc_sum_2.profiler

        p1 = calc_sum_2.profiler
        calc_sum_2(10000)
        p2 = calc_sum_2.profiler
        p2.print_stats()
        assert p1 is p2

    @staticmethod
    def test_memory_profiler_wraps():
        """测试内存分析器的名称&文档串替换"""
        assert calc_sum.__name__ == 'calc_sum'
        assert calc_sum_2.__name__ == 'calc_sum_2'

        assert calc_sum.__doc__ == '求和计算'
        assert calc_sum_2.__doc__ == '求和计算'

        assert isinstance(calc_sum, MemoryProfiler)
        assert isinstance(calc_sum_2, MemoryProfiler)

    @staticmethod
    def test_memory_profiler_with_force_new_profiler():
        """测试强制使用新分析器的参数功能"""

        @MemoryProfiler(print_res=False, force_new_profiler=True)
        def _force_new_profiler():
            pass

        _force_new_profiler()
        p1 = _force_new_profiler.profiler
        _force_new_profiler()
        p2 = _force_new_profiler.profiler
        assert p1 is not p2


if __name__ == '__main__':
    TestMemoryProfilerToFunction.test_memory_profiler_call()
