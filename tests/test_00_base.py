# encoding=utf8
"""
测试基础函数包
"""
import logging

import pytest

from moprofiler import base

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
LOG = logging.getLogger(__name__)


class A(object):  # pylint: disable=C0111
    def test(self):  # pylint: disable=C0111
        pass


class TestBase(object):
    """测试基础函数包"""

    @staticmethod
    def test_get_default_key():
        """测试获取默认的键名函数"""
        expect_name = '{name}-A-test'.format(name=__name__)
        a = A()
        assert base.get_default_key(a, a.test) == expect_name
        assert base.get_default_key(A, A.test) == expect_name
        with pytest.raises(TypeError):
            print base.get_default_key(a, 1)
