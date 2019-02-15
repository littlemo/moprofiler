# encoding=utf8
"""
测试时间分析器
"""
import random

from line_profiler import LineProfiler

from moprofiler import TimeProfiler


@TimeProfiler
def _judge_with_set(x):
    """test_wrapper_set_docstring"""
    cnt = 0
    tp = {'1', '3', '5', '7', '11'}
    for i in x:
        if i in tp:
            cnt += 1
    return cnt

@TimeProfiler(print_res=False, fake_method=True)
def _judge_with_list(x):
    """test_wrapper_list_docstring"""
    cnt = 0
    tp = ['1', '3', '5', '7', '11']
    for i in x:
        if i in tp:
            cnt += 1
    return cnt


class TestTimeProfilerToFunction(object):
    """测试用于装饰函数的时间分析器"""

    @staticmethod
    def test_time_profiler_call():
        """测试时间分析器装饰器调用"""
        assert isinstance(_judge_with_set.profiler, LineProfiler)
        assert isinstance(_judge_with_list.profiler, LineProfiler)

        random_list = [random.choice(['2', '11']) for _x in range(1000)]
        _judge_with_set(random_list)
        assert _judge_with_set(random_list) == _judge_with_list(random_list)

        assert isinstance(_judge_with_set.profiler, LineProfiler)
        assert isinstance(_judge_with_list.profiler, LineProfiler)
        assert _judge_with_set.profiler is not _judge_with_list.profiler

        p1 = _judge_with_list.profiler
        p1.print_stats()
        _judge_with_list(random_list)
        p2 = _judge_with_list.profiler
        assert p1 is p2

    @staticmethod
    def test_time_profiler_wraps():
        """测试时间分析器的名称&文档串替换"""
        assert _judge_with_set.__name__ == '_judge_with_set'
        assert _judge_with_list.__name__ == '_judge_with_list'

        assert _judge_with_set.__doc__ == 'test_wrapper_set_docstring'
        assert _judge_with_list.__doc__ == 'test_wrapper_list_docstring'

        assert isinstance(_judge_with_set, TimeProfiler)
        assert isinstance(_judge_with_list, TimeProfiler)

    @staticmethod
    def test_time_profiler_with_force_new_profiler():
        """测试强制使用新分析器的参数功能"""

        @TimeProfiler(print_res=False, force_new_profiler=True)
        def _force_new_profiler():
            pass

        _force_new_profiler()
        p1 = _force_new_profiler.profiler
        _force_new_profiler()
        p2 = _force_new_profiler.profiler
        assert p1 is not p2
