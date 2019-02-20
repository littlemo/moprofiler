# encoding=utf8
"""
提供用于性能分析的相关基类&函数定义
"""
import abc
import inspect
import logging
import types
from contextlib import contextmanager
from functools import update_wrapper

import six
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
        if isinstance(
                closure.cell_contents,
                (types.FunctionType, types.MethodType)):  # pragma: no cover
            func = closure.cell_contents
            return get_callargs(func, *args, **kwargs)
    else:  # pylint: disable=W0120
        callargs = inspect.getcallargs(func, *args, **kwargs)
        return callargs


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


class ClassDecoratorBase(object):
    """
    通用类装饰器基类
    """
    def __init__(self, _function=None, fake_method=True):
        """
        类装饰器初始化

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param bool fake_method: 是否将被装饰后的类装饰器伪装成方法，默认为是。
            注意，伪装后仍然可以正常调用类装饰器中额外定义的对象属性，
            此参数仅用于装饰类方法时使用，装饰函数时无效
        """
        # 被装饰函数/方法
        self.__func = None
        self.__instance = None
        _invoked = bool(_function and callable(_function))
        self.func = _function if _invoked \
            else None  # type: types.FunctionType or types.MethodType

        # 装饰器参数
        self.__fake_method = fake_method

    @property
    def func(self):
        """被封装函数的 getter 方法"""
        return self.__func

    @func.setter
    def func(self, func):
        """被封装函数的 setter 方法"""
        if func:
            update_wrapper(self, func)
        self.__func = func

    def __call__(self, *args, **kwargs):
        """
        :rtype: ClassDecoratorBase
        """
        _func = self.func
        if not self.func:
            self.func = args[0]
        if not self.__fake_method and self.__instance:
            args = (self.__instance,) + args
        return self if not _func else self._wrapper(*args, **kwargs)

    def __get__(self, *args, **kwargs):
        self.__instance = args[0]
        return six.create_bound_method(self, self.__instance) if self.__fake_method else self

    @abc.abstractmethod
    def _wrapper(self, *args, **kwargs):
        """用于执行调用被封装方法"""


class ProfilerClassDecorator(ClassDecoratorBase):
    """
    分析器的类装饰器
    """
    @abc.abstractproperty
    def profiler_factory(self):
        """用于生产分析器的工厂"""

    def __init__(
            self, _function=None, print_res=True, force_new_profiler=False,
            profiler_args=None, profiler_kwargs=None, **kwargs):
        """
        分析器的类装饰器初始化

        增加分析器相关的供外部使用的公共属性

        :param _function: 被封装的对象，由解释器自动传入，不需关心
        :type _function: types.FunctionType or types.MethodType
        :param bool print_res: 是否在被装饰对象退出后立刻打印分析结果，默认为 ``True`` 。
            当需要将多次调用结果聚集后输出时，可设为 ``False`` ，并通过调用被装饰函数/方法
            （装饰后将被替换为 :py:class:`~moprofiler.base.ProfilerClassDecorator` ）的
            :py:meth:`~moprofiler.base.ProfilerClassDecorator.print_stats` 方法进行结果输出
        :param bool force_new_profiler: 是否强制使用新的分析器，默认为 ``否``
        :param tuple profiler_args: 分析器工厂的位置参数列表
        :param dict profiler_kwargs: 分析器工厂的关键字参数字典
        """
        super(ProfilerClassDecorator, self).__init__(_function=_function, **kwargs)

        self.profiler = None  #: 分析器实例对象
        self.profiler_args = profiler_args or ()
        self.profiler_kwargs = profiler_kwargs or {}

        self._print_res = print_res
        self._force_new_profiler = force_new_profiler

        self.__init_profiler_from_factory()

    def __init_profiler_from_factory(self):
        """从工厂实例化分析器"""
        if self._force_new_profiler or not self.profiler:
            self.profiler = self.profiler_factory(
                *self.profiler_args, **self.profiler_kwargs)

    def __call__(self, *args, **kwargs):
        """
        :rtype: ProfilerClassDecorator
        """
        self.__init_profiler_from_factory()
        return super(ProfilerClassDecorator, self).__call__(*args, **kwargs)

    def _wrapper(self, *args, **kwargs):
        profiler_wrapper = self.profiler(self.func)
        res = profiler_wrapper(*args, **kwargs)

        # 此处由于 LineProfiler 的 C 库造成的 coverage 统计 Bug ，故手动配置为 no cover
        if self._print_res:
            self.print_stats()
        return res

    @abc.abstractmethod
    def print_stats(self):
        """
        打印统计结果

        抽象方法，需子类实现
        """
