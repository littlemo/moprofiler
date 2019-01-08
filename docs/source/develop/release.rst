.. _develop-release:

========
发布说明
========

1.0.1 (2019-01-08 19:27:20)
---------------------------

Feature
~~~~~~~

#. 为秒表工具增加内存监控的功能，便于查看两个打点间的内存变化


1.0.0 (2019-01-05 21:13:20)
---------------------------

Feature
~~~~~~~

#. 实现对 `line_profiler`_ 封装的装饰器及相应的 :py:class:`~moprofiler.time.TimeProfilerMixin` 类
#. 实现对 `memory-profiler`_ 封装的装饰器及相应的 :py:class:`~moprofiler.memory.MemoryProfilerMixin` 类
#. 实现用于打点计时的秒表工具，方便记录函数的关键执行节点，以及耗时


.. _line_profiler: https://github.com/rkern/line_profiler
.. _memory-profiler: https://github.com/pythonprofilers/memory_profiler
