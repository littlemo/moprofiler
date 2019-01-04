# encoding=utf8
"""
提供用于性能分析的相关基类&函数定义
"""
import inspect
import logging
from contextlib import contextmanager
from types import FunctionType

from pyaop import AOP, Proxy, Return

LOG = logging.getLogger(__name__)


def proxy(obj, prop, prop_name):
    """
    为 object 对象代理一个属性

    :param object obj: 被代理的对象
    :param object prop: 代理返回的属性
    :param str prop_name: 被代理的属性名
    :return: 被代理之后的对象
    :rtype: object
    """
    def common(_proxy, name, value=None):  # pylint: disable=W0613
        """
        用于 Hook 的钩子函数
        """
        if name == prop_name:
            Return(prop)

    return Proxy(obj, before=[
        AOP.Hook(common, ["__getattribute__", "__setattr__", "__delattr__"]),
    ])


def get_callargs(func, *args, **kwargs):
    """
    找到层层装饰器下最里层的函数的 callargs

    :param function func: 被装饰过的函数
    :param list args: 调用函数时的位置参数
    :param dict kwargs: 调用函数时的关键字参数
    :return: 调用参数字典
    :rtype: dict
    """
    for closure in func.__closure__ or []:
        if isinstance(closure.cell_contents, FunctionType):
            func = closure.cell_contents
            return get_callargs(func, *args, **kwargs)
    else:  # pylint: disable=W0120
        callargs = inspect.getcallargs(func, *args, **kwargs)
        spec = inspect.getargspec(func)

        if spec.keywords:
            callargs.update(callargs.pop(spec.keywords, {}))

        return callargs


def get_default_key(self_or_cls, func):
    """
    获取默认的键名

    生成规则 "模块名-类名-方法名"

    :param object self_or_cls: 对象或类
    :param func: 方法或方法名
    :type func: FunctionType or str
    :return: 键名
    :rtype: str
    """
    if isinstance(self_or_cls, type):
        key_list = [self_or_cls.__module__, self_or_cls.__name__]
    else:
        key_list = [self_or_cls.__module__, self_or_cls.__class__.__name__]
    func_name = func.__name__ if hasattr(func, '__name__') else func
    if not isinstance(func_name, str):
        raise TypeError('func 参数的类型错误！{}'.format(type(func)))
    key_list.append(func_name)
    return '-'.join(key_list)


def is_instance_or_subclass(self_or_cls, super_cls):
    """
    判断对象或类是否继承了指定类

    :param object self_or_cls: 对象或类
    :param class super_cls: 父类
    :return: 判断结果
    :rtype: bool
    """
    return (
        isinstance(self_or_cls, super_cls) or
        (isinstance(self_or_cls, type) and issubclass(self_or_cls, super_cls)))


class ProfilerMixin(object):
    """
    分析器 Mixin 的基类
    """
    @classmethod
    @contextmanager
    def _get_profiler(cls, self_or_cls, **callargs):  # pylint: disable=W0613
        """
        子类需要通过 super 调用父类的 _get_profiler 方法获取代理了指定分析器的 Proxy 对象

        :param object self_or_cls: 被代理的对象 or 类
        :param dict callargs: 调用该上下文管理器时传入的所有调用参数
        :return: 返回 Proxy 对象
        :rtype: Iterator[Proxy]
        """
        yield self_or_cls
