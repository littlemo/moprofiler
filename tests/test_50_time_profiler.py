# encoding=utf8
"""
测试时间分析器
"""
import random

from moprofiler import time, time_profiler, time_profiler_getter


class TestTimeProfiler(object):
    """测试用于装饰函数的时间分析器"""

    @staticmethod
    def test_time_profiler():
        """测试时间分析器装饰器"""

        @time_profiler
        def _judge_with_set(x):
            cnt = 0
            tp = {'1', '3', '5', '7', '11'}
            for i in x:
                if i in tp:
                    cnt += 1
            return cnt

        @time_profiler(print_res=False)
        def _judge_with_list(x):
            cnt = 0
            tp = ['1', '3', '5', '7', '11']
            for i in x:
                if i in tp:
                    cnt += 1
            return cnt

        random_list = [random.choice(['2', '11']) for _x in range(1000)]
        assert _judge_with_set(random_list) == _judge_with_list(random_list)
        _judge_with_list(random_list)
        print('时间分析器暂存池：{}'.format(getattr(time, '__time_profiler_pool').keys()))
        p1 = time_profiler_getter('_judge_with_list')
        p1.print_stats()
        _judge_with_list(random_list)
        p2 = time_profiler_getter('_judge_with_list')
        assert p1 is p2

    @staticmethod
    def test_time_profiler_with_force_new_profiler():
        """测试强制使用新分析器的参数功能"""

        @time_profiler(print_res=False, force_new_profiler=True)
        def _force_new_profiler():
            pass

        _force_new_profiler()
        p1 = time_profiler_getter('_force_new_profiler')
        _force_new_profiler()
        p2 = time_profiler_getter('_force_new_profiler')
        assert p1 is not p2
