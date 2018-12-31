# encoding=utf8
"""
测试内存分析器
"""
from moprofiler import memory_profiler


@memory_profiler
def calc_sum():
    """求和计算"""
    _sum = 0
    for _item in range(10000):
        _sum += 1
    return _sum


class TestMemoryProfiler(object):
    """测试用于装饰函数的内存分析器"""

    @staticmethod
    def test_memory_profiler():
        """测试内存分析器装饰器"""
        # 此处由于内存计算处理的加载机制问题，在单测中无法正常统计到
        print('求和结果: {}'.format(calc_sum()))


if __name__ == '__main__':
    print('求和结果: {}'.format(calc_sum()))
