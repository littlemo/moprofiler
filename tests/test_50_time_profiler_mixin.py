# encoding=utf8
"""
测试时间分析器 Mixin
"""
import pytest
from line_profiler import LineProfiler

from moprofiler import TimeProfilerMixin, time, time_profiler


class QuickSort(TimeProfilerMixin):
    """
    快速排序
    """
    def __init__(self, arr):
        self.arr = arr

    @time_profiler(name='quick_sort', print_res=False)
    def sort(self, left=None, right=None):
        """排序"""
        left = 0 if not isinstance(left, (int, float)) else left
        right = len(self.arr) - 1 if not isinstance(right, (int, float)) else right
        if left < right:
            partition_index = self.partition(left, right)
            self.sort(left, partition_index - 1)
            self.sort(partition_index + 1, right)

    @time_profiler(print_res=False)
    def partition(self, left, right):
        """分区"""
        pivot = left
        index = pivot + 1
        i = index
        while i <= right:
            if self.arr[i] < self.arr[pivot]:
                self.swap(i, index)
                index += 1
            i += 1
        self.swap(pivot, index - 1)
        return index - 1

    # @time_profiler
    def swap(self, i, j):
        """交换"""
        self.arr[i], self.arr[j] = self.arr[j], self.arr[i]


class TestTimeProfilerMixin(object):
    """测试用于装饰方法的时间分析器"""

    @staticmethod
    def test_time_profiler_mixin():
        """测试时间分析器的 mixin"""
        unsort_list = [3, 12, 12, 11, 15, 9, 12, 4, 15, 4, 2, 15, 7, 10, 12, 2, 3, 1, 14, 5, 7]
        print('\n乱序列表：{}'.format(unsort_list))
        qs = QuickSort(unsort_list)
        qs.sort()
        print('排序列表：{}'.format(qs.arr))
        print('时间分析器暂存池：{}'.format(getattr(time, '__time_profiler_pool').keys()))
        assert isinstance(qs.time_profiler('partition'), LineProfiler)

        # qs.time_profiler('quick_sort').print_stats()
        qs.time_profiler('partition').print_stats()
        # qs.time_profiler('swap').print_stats()

    @staticmethod
    def test_time_profiler_key_error():
        """测试获取不存在的时间分析器"""
        qs = QuickSort([3, 2, 1])
        qs.time_profiler('test', raise_except=False)
        qs.time_profiler('test')
        with pytest.raises(KeyError):
            qs.time_profiler('sort')


if __name__ == '__main__':
    TestTimeProfilerMixin.test_time_profiler_mixin()
