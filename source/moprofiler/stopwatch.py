# encoding=utf8
"""
提供用于计时打点的秒表工具
"""
from __future__ import absolute_import

import logging
import time
import types  # pylint: disable=W0611
from contextlib import contextmanager
from functools import wraps

from line_profiler import is_generator

from . import base

LOG = logging.getLogger(__name__)


class Stopwatch(object):
    """秒表类"""
    LOGGING_LEVEL_DEFAULT = logging.INFO
    DOTTING_FMT_DEFAULT = '[性能] 当前耗时({idx}): {current:.4f}s, 累计耗时: {total:.4f}s'
    FINAL_FMT_ARGS_DEFAULT = '[性能] {name}, 参数列表: {args} {kwargs}, 耗时: {use:.4f}s'
    FINAL_FMT_DEFAULT = '[性能] {name}, 耗时: {use:.4f}s'

    def __init__(self):
        self.buf = []  #: 用来存储计时打点时间
        self.dkwargs = {}  #: 用来存储最终输出时使用的变量
        self.dotting_param_pre = {}  #: 用来记录上次打点输出时的参数信息
        self.logger = None  #: 用来日志输出的 logger  # type: logging.Logger
        self.logging_level = None  #: 日志输出级别

    def __call__(self, func, wrap_param):
        """
        装饰一个函数用来启动一个秒表

        :param func: 被装饰的函数 or 方法
        :type func: types.FunctionType or types.MethodType
        :param dict wrap_param: 额外的关键字参数字典
        :return: 装饰后的函数 or 方法
        :rtype: types.FunctionType or types.MethodType
        """
        if is_generator(func):
            wrapper = self.wrap_generator(func, wrap_param)
        else:
            wrapper = self.wrap_function(func, wrap_param)
        return wrapper

    def wrap_generator(self, func, dkwargs):
        """
        封装一个生成器从而使用秒表对其进行观察
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            g = func(*args, **kwargs)
            # The first iterate will not be a .send()
            self.enable_by_count()
            try:
                item = next(g)
            finally:
                self.disable_by_count()
            input = (yield item)
            # But any following one might be.
            while True:
                self.enable_by_count()
                try:
                    item = g.send(input)
                finally:
                    self.disable_by_count()
                input = (yield item)
        return wrapper

    def wrap_function(self, func, wrap_param):
        """
        封装一个函数从而使用秒表对其进行观察

        :param func: 被封装的函数，由解释器自动传入，不需关心
        :type func: types.FunctionType or types.MethodType
        :return: 封装后的方法
        :rtype: types.FunctionType or types.MethodType
        """
        self.logger = wrap_param.get('logger') or LOG  # type: logging.Logger
        self.logging_level = wrap_param.get('logging_level') or self.LOGGING_LEVEL_DEFAULT
        _fmt = wrap_param.get('fmt') or (
            self.FINAL_FMT_ARGS_DEFAULT if wrap_param.get('print_args') else self.FINAL_FMT_DEFAULT)
        self.dkwargs = wrap_param.get('dkwargs')

        @wraps(func)
        def inner(*args, **kwargs):
            """
            在被装饰函数执行前后进行秒表计时
            """
            _begin_time = time.time()
            fmt_dict = {
                'name': wrap_param.get('name') or func.__name__,
                'args': args,
                'kwargs': kwargs,
                'begin_time': _begin_time,
            }
            self.dkwargs.update(fmt_dict)

            self.buf.append(_begin_time)
            result = func(*args, **kwargs)
            _end_time = time.time()
            self.buf.append(_end_time)

            fmt_dict['end_time'] = _end_time
            fmt_dict['use'] = _end_time - _begin_time
            self.dkwargs.update(fmt_dict)

            self.logger.log(self.logging_level, _fmt.format(**self.dkwargs))
            return result
        return inner

    def dotting(self, fmt='', logging_level=None, **kwargs):
        """
        输出打点日志

        该方法的全部参数若不传则使用历史值

        :param str fmt: 用来输出打点日志的格式化模板，需使用 format 的占位符格式
        :param int logging_level: 日志输出级别，默认使用装饰当前方法时设置的级别，若无则使用类属性中定义的默认值
        """
        idx = len(self.buf)
        self.buf.append(time.time())
        _fmt = fmt or self.dotting_param_pre.get('fmt') or self.DOTTING_FMT_DEFAULT
        _level = logging_level or self.dotting_param_pre.get('logging_level') or self.logging_level
        _kwargs = self.dotting_param_pre.get('kwargs', {})  # type: dict
        if not _kwargs:
            _kwargs.update(self.dkwargs)
        _kwargs.update(kwargs)

        self.logger.log(_level, _fmt.format(
            current=self.buf[-1] - self.buf[-2],
            total=self.buf[-1] - self.buf[0],
            idx=idx,
            **_kwargs))

        _kwargs['fmt'] = _fmt
        _kwargs['logging_level'] = _level


class StopwatchMixin(base.ProfilerMixin):
    """
    秒表 Mixin 类

    用以提供复杂的秒表功能，如：
    - 针对需要多次调用的方法进行累加记录的场景
    - 在一次代码执行流程中同时记录多个方法，并灵活控制记录结果的输出
    """
    stopwatch = None  # type: Stopwatch

    @classmethod
    @contextmanager
    def _get_stopwatch(cls, self_or_cls, **callargs):
        """
        获取秒表对象

        :param object self_or_cls: 被代理的对象 or 类
        :param dict callargs: 调用该上下文管理器时传入的所有调用参数
        :return: 返回被代理的对象 or 类
        :rtype: Iterator[base.Proxy]
        """
        with super(StopwatchMixin, cls)._get_profiler(
            self_or_cls, **callargs) as _self_or_cls:
            yield base.proxy(
                _self_or_cls,
                prop_name='stopwatch',
                prop=Stopwatch())

    @staticmethod
    def stopwatch_manager(  # pylint: disable=R0913
            function=None, print_args=False, logger=None,
            fmt='', name='', logging_level=logging.INFO, **dkwargs):
        """
        返回秒表监控下的函数或方法

        通过额外的关键字参数，支持配置自定义的值到输出模板中

        :param function: 被封装的函数，由解释器自动传入，不需关心
        :type function: types.FunctionType or types.MethodType
        :param bool print_args: 是否打印被装饰函数的参数列表，若含有较长的参数，可能造成日志过长，开启时请注意
        :param logging.Logger logger: 可传入指定的日志对象，便于统一输出样式，默认使用该模块中的全局 logger
        :param str fmt: 用于格式化输出的模板，可在了解所有内置参数变量后自行定制输出样式，若指定该参数则会忽略 print_args
        :param str name: 关键字参数，被装饰方法代理生成的 _stopwatch 所使用的名称，默认为使用被装饰方法的方法名
        :param int logging_level: 打印日志的级别，默认为 INFO
        :return: 装饰后的函数
        :rtype: types.FunctionType or types.MethodType
        """
        invoked = bool(function and callable(function))
        if invoked:
            func = function  # type: types.FunctionType or types.MethodType
        wrap_param = {
            'print_args': print_args,
            'logger': logger,
            'fmt': fmt,
            'name': name,
            'logging_level': logging_level,
            'dkwargs': dkwargs,
        }

        def wrapper(func):
            """
            装饰器封装函数

            :param types.MethodType func: 被装饰方法
            :return: 封装后的方法
            :rtype: types.MethodType
            """
            @wraps(func)
            def inner_function(*args, **kwargs):
                """
                使用秒表封装函数
                """
                _stopwatch_wrapper = Stopwatch()(func, wrap_param)
                return _stopwatch_wrapper(*args, **kwargs)

            @wraps(func)
            def inner_method(self_or_cls, *args, **kwargs):
                """
                使用秒表封装方法

                将被封装方法所用的 self_or_cls 进行代理，从而在方法内可以访问到被代理的 stopwatch 属性

                :param StopwatchMixin self_or_cls: 秒表 Mixin
                """
                callargs = base.get_callargs(func, self_or_cls, *args, **kwargs)
                callargs.pop("cls", None)
                with self_or_cls._get_stopwatch(self_or_cls, **callargs) as _self_or_cls:
                    _stopwatch_wrapper = _self_or_cls.stopwatch(func, wrap_param)
                    return _stopwatch_wrapper(_self_or_cls, *args, **kwargs)

            return inner_function if isinstance(func, types.FunctionType) else inner_method
        return wrapper if not invoked else wrapper(func)


stopwatch = StopwatchMixin.stopwatch_manager
