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

如开始的介绍，本工具集主要由三个子工具 :ref:`overview-time-profiler` ,
:ref:`overview-memory-profiler` , :ref:`overview-stopwatch` 组成，
下面将对其使用方式进行逐一介绍

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

.. _overview-time-profiler:

时间分析器
----------

该分析器可以统计出指定函数或方法中每行代码的执行时间消耗，从而找到瓶颈所在，用例如下:

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
    print('结果: {}'.format(qs.arr))

执行结果如下::

    Timer unit: 1e-06 s

    Total time: 0.000344 s
    File: tests/test_04_time_profiler_mixin.py
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

.. _overview-memory-profiler:

内存分析器
----------

该分析器可以统计出指定函数或方法中每行代码的执行内存消耗，从而找到瓶颈所在，用例如下:

.. code-block:: python

    from moprofiler import MemoryProfilerMixin, memory_profiler


    class MemoryWaste(MemoryProfilerMixin):
        """
        浪费内存
        """
        @memory_profiler(name='wuwuwu', print_res=False)
        def list_waste(self):
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

    mw = MemoryWaste()
    x = mw.list_waste()
    mw.dict_waste(x)
    mw.memory_profiler('wuwuwu').print_stats()

执行结果如下::

    Filename: tests/test_01_memory_profiler_mixin.py

    Line #    Mem usage    Increment   Line Contents
    ================================================
        23     40.9 MiB     40.9 MiB       @classmethod
        24                                 @memory_profiler
        25                                 def dict_waste(cls, a):
        26                                     """字典"""
        27     40.9 MiB      0.0 MiB           ret = {}
        28     40.9 MiB      0.0 MiB           for i in a:
        29     40.9 MiB      0.0 MiB               ret[i] = i
        30     40.9 MiB      0.0 MiB           return ret


    Filename: tests/test_01_memory_profiler_mixin.py

    Line #    Mem usage    Increment   Line Contents
    ================================================
        15     38.6 MiB     38.6 MiB       @memory_profiler(name='wuwuwu', print_res=False)
        16                                 def list_waste(self):
        17                                     """列表"""
        18     39.4 MiB      0.8 MiB           a = [1] * (10 ** 5)
        19     40.9 MiB      1.5 MiB           b = [2] * (2 * 10 ** 5)
        20     40.9 MiB      0.0 MiB           del b
        21     40.9 MiB      0.0 MiB           return a

.. _overview-stopwatch:

秒表工具
--------

该秒表工具可以监控指定函数或方法的执行用时，当被装饰的方法继承了 :py:class:`~moprofiler.stopwatch.StopwatchMixin`
后，可以通过调用 :py:meth:`~moprofiler.stopwatch.Stopwatch.dotting` 方法来进行日志打点，从而记录某个代码切片的用时。

由于打点多少可由开发者自行控制，故该工具与前述 :ref:`overview-time-profiler` 的优势是，可用于生产环境。

.. code-block:: python

    import logging
    import time

    from moprofiler import StopwatchMixin, stopwatch

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
    LOG = logging.getLogger(__name__)


    class zzz(StopwatchMixin):
        """测试方法装饰"""

        @staticmethod
        @stopwatch
        def orz_staticmethod():
            """静态方法"""
            for _i in range(2):
                time.sleep(0.25)

        @stopwatch
        def orz_instancemethod(self, x):
            """实例方法"""
            for _i in range(x):
                self.stopwatch.dotting()
                time.sleep(0.1)
            self.stopwatch.dotting()

        @classmethod
        @stopwatch(
            fmt='[性能] {name}, 参数列表: {args} {kwargs}, 耗时: {use:.8f}s, {foo}',
            logger=LOG,
            name='hakula',
            foo='matata')
        def orz_classmethod(cls, x):
            """类方法"""
            for _i in range(x):
                cls.stopwatch.dotting('定制打点输出{idx}，当前 {current:.8f}s，累计: {total:.8f}s')
                time.sleep(0.1)
            cls.stopwatch.dotting()

        @stopwatch
        def orz_instancemethod_generator(self, x):
            """实例方法生成器"""
            for _i in range(x):
                mute = True if _i == 2 else False
                self.stopwatch.dotting(mute=mute)
                time.sleep(0.1)
                yield _i
            self.stopwatch.dotting()

    z = zzz()
    z.orz_staticmethod()
    z.orz_instancemethod(5)
    z.orz_classmethod(5)
    _tmp = [i for i in z.orz_instancemethod_generator(5)]
    assert _tmp == [i for i in range(5)]

执行结果如下::

    [2019-01-05 22:35:13,680] INFO [moprofiler.stopwatch:147] [性能] orz_staticmethod, 耗时: 0.5071s
    [2019-01-05 22:35:13,681] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(1): 0.0000s, 累计耗时: 0.0000s
    [2019-01-05 22:35:13,786] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(2): 0.1046s, 累计耗时: 0.1046s
    [2019-01-05 22:35:13,891] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(3): 0.1052s, 累计耗时: 0.2098s
    [2019-01-05 22:35:13,997] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(4): 0.1055s, 累计耗时: 0.3153s
    [2019-01-05 22:35:14,101] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(5): 0.1044s, 累计耗时: 0.4197s
    [2019-01-05 22:35:14,205] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(6): 0.1039s, 累计耗时: 0.5236s
    [2019-01-05 22:35:14,205] INFO [moprofiler.stopwatch:147] [性能] orz_instancemethod, 耗时: 0.5238s
    [2019-01-05 22:35:14,205] INFO [test_02_stopwatch_mixin:177] 定制打点输出1，当前 0.00001907s，累计: 0.00001907s
    [2019-01-05 22:35:14,310] INFO [test_02_stopwatch_mixin:177] 定制打点输出2，当前 0.10435295s，累计: 0.10437202s
    [2019-01-05 22:35:14,415] INFO [test_02_stopwatch_mixin:177] 定制打点输出3，当前 0.10521197s，累计: 0.20958400s
    [2019-01-05 22:35:14,519] INFO [test_02_stopwatch_mixin:177] 定制打点输出4，当前 0.10429406s，累计: 0.31387806s
    [2019-01-05 22:35:14,623] INFO [test_02_stopwatch_mixin:177] 定制打点输出5，当前 0.10339808s，累计: 0.41727614s
    [2019-01-05 22:35:14,727] INFO [test_02_stopwatch_mixin:177] 定制打点输出6，当前 0.10414290s，累计: 0.52141905s
    [2019-01-05 22:35:14,727] INFO [test_02_stopwatch_mixin:147] [性能] hakula, 参数列表: (<class 'test_02_stopwatch_mixin.zzz'>, 5) {}, 耗时: 0.52167416s, matata
    [2019-01-05 22:35:14,728] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(1): 0.0000s, 累计耗时: 0.0000s
    [2019-01-05 22:35:14,829] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(2): 0.1010s, 累计耗时: 0.1011s
    [2019-01-05 22:35:15,037] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(4): 0.1040s, 累计耗时: 0.3091s
    [2019-01-05 22:35:15,139] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(5): 0.1025s, 累计耗时: 0.4115s
    [2019-01-05 22:35:15,242] INFO [moprofiler.stopwatch:177] [性能] 当前耗时(6): 0.1029s, 累计耗时: 0.5144s
    [2019-01-05 22:35:15,242] INFO [moprofiler.stopwatch:124] [性能] orz_instancemethod_generator, 耗时: 0.5147s


.. _MoProfiler: https://github.com/littlemo/moprofiler
