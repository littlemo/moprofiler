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

    @classmethod
    def test_closure(cls, a, b=2, *args, **kwargs):
        return a + b

    @classmethod
    def closure_method(cls, func):
        def inner(*args, **kwargs):
            return func
        return inner

    def __call__(self, func):
        def inner(*args, **kwargs):
            return func
        return inner


test_a = A()


def test_closure(a, b=2, *args, **kwargs):
    return a + b


def closure_1(func):
    def inner(*args, **kwargs):
        return func
    return inner


def closure_2(func):
    def inner(*args, **kwargs):
        return func
    return inner


def closure_2_method(func):
    return A.closure_method(func)


def closure_3_call(func):
    return test_a(func)


test_closure = closure_2(closure_1(test_closure))
test_closure_method = closure_2_method(A.test_closure)
test_closure_call = closure_3_call(test_closure)


class TestBase(object):
    """测试基础函数包"""

    @staticmethod
    def test_get_callargs():
        """测试获取调用参数字典的函数"""
        expect = {'a': 10, 'b': 20, 'args': (1, 2), 'kwargs': {'e': 'e', 'd': 'd'}}
        assert expect == base.get_callargs(test_closure, 10, 20, 1, 2, e='e', d='d')
        callargs = base.get_callargs(test_closure_method, 10, 20, 1, 2, e='e', d='d')
        callargs.pop('cls', None)
        assert expect == callargs
        assert expect == base.get_callargs(test_closure_call, 10, 20, 1, 2, e='e', d='d')
