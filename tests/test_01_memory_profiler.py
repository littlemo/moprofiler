# encoding=utf8
"""
测试内存分析器
"""
import gc

from moprofiler import memory_profiler, memory_profiler_getter


@memory_profiler
def calc_sum():
    """求和计算"""
    _sum = 0
    for _item in range(10000):
        _sum += 1
    return _sum


@memory_profiler(print_res=False)
def calc_sum_2(x=10000):
    """求和计算"""
    _sum = 0
    for _item in range(x):
        _sum += 1
    return _sum


class TestMemoryProfiler(object):
    """测试用于装饰函数的内存分析器"""

    @staticmethod
    def test_memory_profiler():
        """测试内存分析器装饰器"""
        # 此处由于内存计算处理的加载机制问题，在单测中无法正常统计到
        print('求和结果: {}'.format(calc_sum()))
        gc.collect()
        calc_sum_2(10000)
        calc_sum_2(10000)
        memory_profiler_getter('calc_sum_2').print_stats()


if __name__ == '__main__':
    TestMemoryProfiler.test_memory_profiler()
