# encoding=utf8
"""
测试秒表 Mixin
"""
import logging
import random
import time

from moprofiler import StopwatchMixin, stopwatch

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
LOG = logging.getLogger(__name__)


class zzz(StopwatchMixin):
    """测试类装饰"""

    @staticmethod
    @stopwatch
    def orz():
        """测试对象方法装饰"""
        for _i in range(2):
            time.sleep(0.5)

    @stopwatch
    def judge_with_set(self, x):
        cnt = 0
        tp = {'1', '3', '5', '7', '11'}
        for i in x:
            self.stopwatch.dotting()
            if i in tp:
                cnt += 1
        return cnt

    @classmethod
    @stopwatch(
        fmt='[性能] {name}, 参数列表: {args} {kwargs}, 耗时: {use:.8f}s, {foo}',
        logger=LOG,
        name='hakula',
        foo='matata')
    def judge_with_list(cls, x):
        cnt = 0
        tp = ['1', '3', '5', '7', '11']
        for i in x:
            cls.stopwatch.dotting('定制打点输出{idx}，当前 {current:.8f}s，累计: {total:.8f}s')
            if i in tp:
                cnt += 1
        cls.stopwatch.dotting()
        return cnt


class TestStopwatch(object):
    """测试用于装饰函数的秒表"""

    @staticmethod
    def test_stopwatch():
        """测试秒表装饰器"""
        random_list = [random.choice(['2', '11']) for _x in range(5)]
        z = zzz()
        ret_set = z.judge_with_set(random_list)
        ret_list = z.judge_with_list(random_list)
        assert ret_set == ret_list
        zzz().orz()


if __name__ == '__main__':
    TestStopwatch.test_stopwatch()
