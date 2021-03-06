.. _develop-release:

========
发布说明
========

1.1.0 (2019-02-20 13:42:05)
---------------------------

Feature
~~~~~~~

#. 重构时间&内存分析器的设计，去除 ``Mixin`` 类，简化使用方法


1.0.3 (2019-01-27 13:47:22)
---------------------------

Feature
~~~~~~~

#. 为时间&内存分析器的装饰器增加 ``force_new_profiler`` 关键字参数，实现强制使用新分析器的功能


1.0.2 (2019-01-13 22:12:14)
---------------------------

Feature
~~~~~~~

#. 实现对函数&静态方法使用 ``时间分析器`` 装饰后，在外部打印分析结果的功能
#. 实现对函数&静态方法使用 ``内存分析器`` 装饰后，在外部打印分析结果的功能

Bugfix
~~~~~~

#. 修复 CI 过程中设置全局包版本号环境变量失败的 Bug


1.0.1.post0 (2019-01-13 15:53:12)
---------------------------------

Optimize
~~~~~~~~

#. 优化 ``rtfd`` 文档编写
#. 完善 ``Travis CI`` 配置，并整理徽章
#. 添加 ``SonarCloud`` 代码质量分析 CI
#. 完善单元测试覆盖率


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
