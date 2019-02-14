# encoding=utf8
"""
测试时间分析器 Mixin
"""
from line_profiler import LineProfiler

from moprofiler import time_profiler


class QuickSort(object):
    """
    快速排序
    """
    def __init__(self, arr):
        self.arr = arr

    @time_profiler(print_res=False)
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


class TestTimeProfilerToMethod(object):
    """测试用于装饰方法的时间分析器"""

    @staticmethod
    def test_time_profiler_run():
        """测试类装饰方法的时间分析器的执行"""
        unsort_list = [3, 12, 12, 11, 15, 9, 12, 4, 15, 4, 2, 15, 7, 10, 12, 2, 3, 1, 14, 5, 7]
        print('\n乱序列表：{}'.format(unsort_list))
        qs = QuickSort(unsort_list)
        print(12121212121, qs.sort)
        qs.sort()
        print('排序列表：{}'.format(qs.arr))

        assert qs.sort.__name__ == 'sort'
        assert qs.partition.__name__ == 'partition'

        assert qs.sort.__doc__ == '排序'
        assert qs.partition.__doc__ == '分区'

        assert isinstance(qs.sort.profiler, LineProfiler)
        assert isinstance(qs.partition.profiler, LineProfiler)

        qs.sort.profiler.print_stats()
        qs.partition.profiler.print_stats()
        # qs.swap.profiler.print_stats()
