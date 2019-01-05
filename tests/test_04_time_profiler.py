# encoding=utf8
"""
测试时间分析器
"""
import random

from moprofiler import time_profiler


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

        @time_profiler
        def _judge_with_list(x):
            cnt = 0
            tp = ['1', '3', '5', '7', '11']
            for i in x:
                if i in tp:
                    cnt += 1
            return cnt

        random_list = [random.choice(['2', '11']) for _x in range(1000)]
        assert _judge_with_set(random_list) == _judge_with_list(random_list)
