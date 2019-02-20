.. _intro-overview:

====
概览
====

`MoProfiler`_ 是一个综合性能分析工具，支持内存分析、时间分析、秒表打点等功能。
可以有效量化 Python 代码的性能，从而找到性能瓶颈所在，使性能优化可以有的放矢。

安装方法
========

您可以通过 ``pip`` 进行安装，本包兼容 ``Python 2.7`` & ``Python 3.5`` ::

    pip install moprofiler>=1.1.0

使用说明
========

如开始的介绍，本工具集主要由三个子工具 :ref:`overview-time-profiler` ,
:ref:`overview-memory-profiler` , :ref:`overview-stopwatch` 组成，
下面将对其使用方式进行逐一介绍

三个子工具分别提供了一个 ``装饰器`` ，其中秒表工具额外提供了一个 ``Mixin`` 类，
一般使用中会存在如下装饰场景:

#. 独立函数
#. 类方法
#. 实例方法
#. 静态方法
#. 生成器方法

为方便使用，三个工具分别提供了一个 ``超级装饰器`` ，即同时支持上述几类场景，
且同时支持 ``有参装饰`` 与 ``无参装饰`` ，当不传参时装饰器后不需增加 ``()``

其中秒表工具，当被装饰对象为 ``类方法`` 或 ``实例方法`` 时，可通过让类继承
:py:class:`~moprofiler.stopwatch.StopwatchMixin` 类，来获得功能增强

.. _overview-time-profiler:

时间分析器
----------

该分析器可以统计出指定函数或方法中每行代码的执行时间消耗，从而找到瓶颈所在，用例如下:

.. code-block:: python

    from moprofiler import TimeProfiler


    class QucikSort(object):
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

        @TimeProfiler(print_res=False)
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

    # 从 1.1.0 版本开始支持的结果打印方式
    qs.partition.print_stats()
    print('结果: {}'.format(qs.arr))

执行结果如下::

    Timer unit: 1e-06 s

    Total time: 0.000344 s
    File: tests/test_50_time_profiler_to_method.py
    Function: partition at line 28

    Line #      Hits         Time  Per Hit   % Time  Line Contents
    ==============================================================
        28                                               @TimeProfiler(print_res=False)
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

.. attention::

   当被装饰函数&方法被多次调用时，会复用该函数&方法对应的单例分析器，
   所得的统计结果在上次的基础上累加后用于打印。若确实不关心累计结果，
   仅需要使用全新的分析器进行分析可在装饰时使用 ``force_new_profiler`` 关键字参数实现，
   具体参考其父类中的定义 :py:class:`~moprofiler.base.ProfilerClassDecorator`

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

.. attention::

   当被装饰函数&方法被多次调用时，会复用该函数&方法对应的单例分析器，
   所得的统计结果在上次的基础上累加后用于打印。若确实不关心累计结果，
   仅需要使用全新的分析器进行分析可在装饰时使用 ``force_new_profiler`` 关键字参数实现，
   具体参考 :py:func:`~moprofiler.memory.memory_profiler`

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
            fmt='[性能] {name}, 参数列表: {args}, 耗时: {time_use:.8f}s, {foo}',
            logger=LOG,
            name='hakula',
            foo='matata')
        def orz_classmethod(cls, x):
            """类方法"""
            for _i in range(x):
                cls.stopwatch.dotting('定制打点输出{idx}，当前 {time_diff:.8f}s，累计: {time_total:.8f}s')
                time.sleep(0.1)
            cls.stopwatch.dotting()

        @stopwatch(print_mem=True)
        def orz_instancemethod_generator(self, x):
            """实例方法生成器"""
            for _i in range(x):
                mute = True if _i == 2 else False
                self.stopwatch.dotting(mute=mute, memory=True)
                time.sleep(0.1)
                yield _i
            self.stopwatch.dotting(memory=True)

    z = zzz()
    z.orz_staticmethod()
    z.orz_instancemethod(5)
    z.orz_classmethod(5)
    _tmp = [i for i in z.orz_instancemethod_generator(5)]
    assert _tmp == [i for i in range(5)]

执行结果如下::

    [2019-01-08 19:13:26,019] INFO [moprofiler.stopwatch:120] [性能] orz_staticmethod, 耗时: 0.5062s
    [2019-01-08 19:13:26,021] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(1): 0.0002s, 累计耗时: 0.0002s
    [2019-01-08 19:13:26,127] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(2): 0.1054s, 累计耗时: 0.1056s
    [2019-01-08 19:13:26,229] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(3): 0.1021s, 累计耗时: 0.2078s
    [2019-01-08 19:13:26,333] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(4): 0.1045s, 累计耗时: 0.3123s
    [2019-01-08 19:13:26,438] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(5): 0.1046s, 累计耗时: 0.4168s
    [2019-01-08 19:13:26,542] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(6): 0.1045s, 累计耗时: 0.5213s
    [2019-01-08 19:13:26,543] INFO [moprofiler.stopwatch:120] [性能] orz_instancemethod, 耗时: 0.5218s
    [2019-01-08 19:13:26,544] INFO [test_02_stopwatch_mixin:214] 定制打点输出1，当前 0.00021791s，累计: 0.00021791s
    [2019-01-08 19:13:26,647] INFO [test_02_stopwatch_mixin:214] 定制打点输出2，当前 0.10304499s，累计: 0.10326290s
    [2019-01-08 19:13:26,751] INFO [test_02_stopwatch_mixin:214] 定制打点输出3，当前 0.10447907s，累计: 0.20774198s
    [2019-01-08 19:13:26,856] INFO [test_02_stopwatch_mixin:214] 定制打点输出4，当前 0.10449409s，累计: 0.31223607s
    [2019-01-08 19:13:26,961] INFO [test_02_stopwatch_mixin:214] 定制打点输出5，当前 0.10524797s，累计: 0.41748405s
    [2019-01-08 19:13:27,065] INFO [test_02_stopwatch_mixin:214] [性能] 当前耗时(6): 0.1044s, 累计耗时: 0.5219s
    [2019-01-08 19:13:27,066] INFO [test_02_stopwatch_mixin:120] [性能] hakula, 参数列表: (<class 'test_02_stopwatch_mixin.zzz'>, 5), 耗时: 0.52235889s, matata
    [2019-01-08 19:13:27,069] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(1): 0.0019s, 累计耗时: 0.0019s, 当前变化:  1M, 累计变化:  1M
    [2019-01-08 19:13:27,175] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(2): 0.1060s, 累计耗时: 0.1079s, 当前变化:  2M, 累计变化:  3M
    [2019-01-08 19:13:27,384] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(4): 0.1041s, 累计耗时: 0.3167s, 当前变化:  2M, 累计变化:  6M
    [2019-01-08 19:13:27,490] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(5): 0.1068s, 累计耗时: 0.4235s, 当前变化:  1M, 累计变化:  7M
    [2019-01-08 19:13:27,594] INFO [moprofiler.stopwatch:214] [性能] 当前耗时(6): 0.1040s, 累计耗时: 0.5274s, 当前变化:  0M, 累计变化:  7M
    [2019-01-08 19:13:27,598] INFO [moprofiler.stopwatch:120] [性能] orz_instancemethod_generator, 耗时: 0.5313s, 内存变化:  7M


.. _MoProfiler: https://github.com/littlemo/moprofiler
