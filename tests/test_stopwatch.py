# encoding=utf8
"""
测试时间分析器
"""
import logging
import random

from moprofiler import stopwatch

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
LOG = logging.getLogger('test_stopwatch')


@stopwatch
def _judge_with_set(x):
    cnt = 0
    tp = {'1', '3', '5', '7', '11'}
    for i in x:
        if i in tp:
            cnt += 1
    return cnt

@stopwatch(
    print_args=True,
    fmt='[性能] {name}, 参数列表: {args} {kwargs}, 耗时: {use:.8f}s, {foo}',
    logger=LOG,
    name='hakula',
    foo='matata')
def _judge_with_list(x):
    cnt = 0
    tp = ['1', '3', '5', '7', '11']
    for i in x:
        if i in tp:
            cnt += 1
    return cnt


class zzz(object):
    """测试类装饰"""
    @stopwatch
    def orz(self):
        """测试对象方法装饰"""
        pass


class TestStopwatch(object):
    """测试用于装饰函数的秒表"""

    @staticmethod
    def test_stopwatch():
        """测试秒表装饰器"""
        random_list = [random.choice(['2', '11']) for _x in range(5)]
        assert _judge_with_set(random_list) == _judge_with_list(random_list)
        zzz().orz()
