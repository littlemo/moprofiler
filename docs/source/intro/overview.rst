.. _intro-overview:

====
概览
====

`MoProfiler`_ 是一个综合性能分析工具，支持内存分析、时间分析、秒表打点等功能。
可以有效量化 Python 代码的性能，从而找到性能瓶颈所在，使性能优化可以有的放矢。

安装方法
========

您可以通过 ``pip`` 进行安装，本包兼容 ``Python 2.7`` & ``Python 3.5`` ::

    pip install moprofiler

使用说明
========

如开始的介绍，本工具集主要由三个子工具组成，下面将对其使用方式进行逐一介绍

三个子工具分别提供了一个 ``装饰器`` 以及一个用于扩充类的 ``Mixin`` 类，
一般使用中会存在如下装饰场景:

#. 独立函数
#. 类方法
#. 实例方法
#. 静态方法

为方便使用，三个工具分别提供了一个 ``超级装饰器`` ，即同时支持上述四类场景，
且同时支持 ``有参装饰`` 与 ``无参装饰`` ，当不传参时装饰器后不需增加 ``()``

当被装饰对象为 ``类方法`` 或 ``实例方法`` 时，可通过让类继承相应的 ``Mixin`` 类，
来获得功能增强，有效减小使用成本

时间分析器
----------

该分析器可以统计出指定函数或方法中每行代码的执行耗时，从而找到瓶颈所在，用例如下:

.. code-block:: python

    from moprofiler import TimeProfilerMixin, time_profiler

    class QucikSort(TimeProfilerMixin):
        """
        快速排序
        """
        def __init__(self, arr):
            self.arr = arr

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

        def swap(self, i, j):
            """交换"""
            self.arr[i], self.arr[j] = self.arr[j], self.arr[i]

    unsort_list = [3, 12, 12, 11, 15, 9, 12, 4, 15, 4, 2, 15, 7, 10, 12, 2, 3, 1, 14, 5, 7]
    qs = QucikSort(unsort_list)
    qs.sort()
    qs.time_profiler('partition').print_stats()
    print('\n结果: {}'.format(qs.arr))

执行结果如下::

    Timer unit: 1e-06 s

    Total time: 0.000344 s
    File: ../tests/test_04_time_profiler_mixin.py
    Function: partition at line 28

    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================
        28                                               @time_profiler(print_res=False)
        29                                               def partition(self, left, right):
        30                                                   """分区"""
        31        15         17.0      1.1      4.9          pivot = left
        32        15         10.0      0.7      2.9          index = pivot + 1
        33        15          7.0      0.5      2.0          i = index
        34        93         63.0      0.7     18.3          while i <= right:
        35        78         58.0      0.7     16.9              if self.arr[i] < self.arr[pivot]:
        36        33         74.0      2.2     21.5                  self.swap(i, index)
        37        33         34.0      1.0      9.9                  index += 1
        38        78         47.0      0.6     13.7              i += 1
        39        15         26.0      1.7      7.6          self.swap(pivot, index - 1)
        40        15          8.0      0.5      2.3          return index - 1

    结果：[1, 2, 2, 3, 3, 4, 4, 5, 7, 7, 9, 10, 11, 12, 12, 12, 12, 14, 15, 15, 15]

内存分析器
----------


秒表工具
--------


.. _MoProfiler: https://github.com/littlemo/moprofiler
