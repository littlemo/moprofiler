# encoding=utf8
"""
测试秒表 Mixin
"""
import logging
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
    def orz_staticmethod():
        """测试对象方法装饰"""
        for _i in range(2):
            time.sleep(0.25)

    @stopwatch
    def orz_instancemethod(self, x):
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
        for _i in range(x):
            cls.stopwatch.dotting('定制打点输出{idx}，当前 {current:.8f}s，累计: {total:.8f}s')
            time.sleep(0.1)
        cls.stopwatch.dotting()


class TestStopwatch(object):
    """测试用于装饰函数的秒表"""

    @staticmethod
    def test_stopwatch():
        """测试秒表装饰器"""
        z = zzz()
        z.orz_staticmethod()
        zzz.orz_staticmethod()
        z.orz_instancemethod(10)
        z.orz_classmethod(10)


if __name__ == '__main__':
    TestStopwatch.test_stopwatch()
