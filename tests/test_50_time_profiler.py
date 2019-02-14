# encoding=utf8
"""
测试时间分析器
"""
import random

from moprofiler import time_profiler


@time_profiler
def _judge_with_set(x):
    """test_wrapper_set_docstring"""
    cnt = 0
    tp = {'1', '3', '5', '7', '11'}
    for i in x:
        if i in tp:
            cnt += 1
    return cnt

@time_profiler(print_res=False)
def _judge_with_list(x):
    """test_wrapper_list_docstring"""
    cnt = 0
    tp = ['1', '3', '5', '7', '11']
    for i in x:
        if i in tp:
            cnt += 1
    return cnt


class TestTimeProfiler(object):
    """测试用于装饰函数的时间分析器"""

    @staticmethod
    def test_time_profiler_run():
        """测试时间分析器装饰器执行"""
        assert _judge_with_set.time_profiler is None
        assert _judge_with_list.time_profiler is None

        random_list = [random.choice(['2', '11']) for _x in range(1000)]
        _judge_with_set(random_list)
        assert _judge_with_set(random_list) == _judge_with_list(random_list)

        p1 = _judge_with_list.time_profiler
        p1.print_stats()
        _judge_with_list(random_list)
        p2 = _judge_with_list.time_profiler
        assert p1 is p2

    @staticmethod
    def test_time_profiler_wraps():
        """测试时间分析器的名称&文档串替换"""
        assert _judge_with_set.__name__ == '_judge_with_set'
        assert _judge_with_list.__name__ == '_judge_with_list'

        assert _judge_with_set.__doc__ == 'test_wrapper_set_docstring'
        assert _judge_with_list.__doc__ == 'test_wrapper_list_docstring'

        assert isinstance(_judge_with_set, time_profiler)
        assert isinstance(_judge_with_list, time_profiler)

    @staticmethod
    def test_time_profiler_with_force_new_profiler():
        """测试强制使用新分析器的参数功能"""

        @time_profiler(print_res=False, force_new_profiler=True)
        def _force_new_profiler():
            pass

        _force_new_profiler()
        p1 = _force_new_profiler.time_profiler
        _force_new_profiler()
        p2 = _force_new_profiler.time_profiler
        assert p1 is not p2
