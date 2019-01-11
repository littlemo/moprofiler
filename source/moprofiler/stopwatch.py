# encoding=utf8
"""
提供用于计时打点的秒表工具
"""
from __future__ import absolute_import

import logging
import os
import time
import types  # pylint: disable=W0611
from contextlib import contextmanager
from functools import wraps

import psutil
from line_profiler import is_generator

from . import base

LOG = logging.getLogger(__name__)


class Stopwatch(object):  # pylint: disable=R0902
    """秒表类"""
    LOGGING_LEVEL_DEFAULT = logging.INFO
    DOTTING_FMT_DEFAULT = '[性能] 当前耗时({idx}): {time_diff:.4f}s, 累计耗时: {time_total:.4f}s'
    DOTTING_FMT_WITH_MEM_DEFAULT = DOTTING_FMT_DEFAULT + \
        ', 当前变化: {mem_diff:2d}M, 累计变化: {mem_total:2d}M'
    FINAL_FMT_ARGS_DEFAULT = '[性能] {name}, 参数列表: {args} {kwargs}, 耗时: {time_use:.4f}s'
    FINAL_FMT_DEFAULT = '[性能] {name}, 耗时: {time_use:.4f}s'
    FINAL_FMT_ARGS_WITH_MEM_DEFAULT = FINAL_FMT_ARGS_DEFAULT + ', 内存变化: {mem_use:2d}M'
    FINAL_FMT_WITH_MEM_DEFAULT = FINAL_FMT_DEFAULT + ', 内存变化: {mem_use:2d}M'

    def __init__(self):
        self.time_buf = []  #: 用来存储计时打点时间
        self.mem_buf = []  #: 用来存储打点内存
        self.name = ''  #: 秒表的名称，可在装饰时设置，默认为使用被装饰方法的方法名
        self.dkwargs = {}  #: 用来存储最终输出时使用的变量
        self.dotting_param_pre = {'kwargs': {}}  #: 用来记录上次打点输出时的参数信息
        #: 用来日志输出的 logger
        self.logger = None  # type: logging.Logger
        self.logging_level = None  #: 日志输出级别
        self.final_fmt = ''  #: 输出最终计时结果的字符串模板
        self.is_print_memory = False  #: 是否打印内存

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

    def _init_param(self, wrap_param):
        """
        初始化对象属性

        :param dict wrap_param: 封装时传入的参数字典
        """
        self.name = wrap_param.get('name')
        self.logger = wrap_param.get('logger') or LOG  # type: logging.Logger
        self.logging_level = wrap_param.get('logging_level') or self.LOGGING_LEVEL_DEFAULT
        self.dkwargs = wrap_param.get('dkwargs')
        self.is_print_memory = wrap_param.get('print_mem') or False
        if self.is_print_memory:
            self.final_fmt = wrap_param.get('fmt') or (
                self.FINAL_FMT_ARGS_WITH_MEM_DEFAULT if wrap_param.get('print_args') else \
                self.FINAL_FMT_WITH_MEM_DEFAULT)
        else:
            self.final_fmt = wrap_param.get('fmt') or (
                self.FINAL_FMT_ARGS_DEFAULT if wrap_param.get('print_args') else \
                self.FINAL_FMT_DEFAULT)

    def _start(self, func, args, kwargs):
        """
        启动秒表

        :param func: 被封装的函数，由解释器自动传入，不需关心
        :type func: types.FunctionType or types.MethodType
        :param list args: 被装饰函数被调用时的位置参数
        :param dict kwargs: 被装饰函数被调用时的关键字参数
        """
        self.name = self.name or func.__name__
        _begin_time = time.time()
        fmt_dict = {
            'name': self.name,
            'args': args,
            'kwargs': kwargs,
            'begin_time': _begin_time,
        }
        self.time_buf.append(_begin_time)

        _begin_mem = self._get_mem_info()
        self.mem_buf.append(_begin_mem)
        fmt_dict['begin_mem'] = _begin_mem

        self.dkwargs.update(fmt_dict)

    def _end(self):
        """
        结束秒表
        """
        _end_time = time.time()
        self.time_buf.append(_end_time)
        self.dkwargs['end_time'] = _end_time
        self.dkwargs['time_use'] = _end_time - self.dkwargs['begin_time']
        if self.is_print_memory:
            _end_mem = self._get_mem_info()
            self.mem_buf.append(_end_mem)
            self.dkwargs['end_mem'] = _end_mem
            self.dkwargs['mem_use'] = _end_mem - self.dkwargs['begin_mem']

        self.logger.log(self.logging_level, self.final_fmt.format(**self.dkwargs))

    @staticmethod
    def _get_mem_info():
        """
        获取内存信息

        :return: 当前进程已用内存(rss)，单位 ``MB``
        :rtype: int
        """
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss >> 20  # 为速度考虑，使用移位操作
        return mem

    def wrap_generator(self, func, wrap_param):
        """
        封装一个生成器从而使用秒表对其进行观察

        :param func: 被封装的函数，由解释器自动传入，不需关心
        :type func: types.FunctionType or types.MethodType
        :param dict wrap_param: 封装时传入的参数字典
        :return: 封装后的方法
        :rtype: types.FunctionType or types.MethodType
        """
        self._init_param(wrap_param)

        @wraps(func)
        def inner(*args, **kwargs):
            """
            在被装饰函数执行前后进行秒表计时
            """
            self._start(func, args, kwargs)

            g = func(*args, **kwargs)
            # 第一次迭代将不调用 send()
            item = next(g)
            _input = (yield item)
            try:
                while True:
                    item = g.send(_input)
                    _input = (yield item)
            except StopIteration:
                self._end()
        return inner

    def wrap_function(self, func, wrap_param):
        """
        封装一个函数从而使用秒表对其进行观察

        :param func: 被封装的函数，由解释器自动传入，不需关心
        :type func: types.FunctionType or types.MethodType
        :param dict wrap_param: 封装时传入的参数字典
        :return: 封装后的方法
        :rtype: types.FunctionType or types.MethodType
        """
        self._init_param(wrap_param)

        @wraps(func)
        def inner(*args, **kwargs):
            """
            在被装饰函数执行前后进行秒表计时
            """
            self._start(func, args, kwargs)
            result = func(*args, **kwargs)
            self._end()
            return result
        return inner

    def dotting(self, fmt='', logging_level=None, memory=False, mute=False, **kwargs):
        """
        输出打点日志

        会在打点时记录当前的时间&进程内存使用(若 ``memory`` 为 ``True``)，并将其与上次的打点记录做差，
        分别获取时间差 ``time_diff`` 、内存差 ``memory_diff`` ，再将其与进入函数时的记录做差，
        分别获取到时间差 ``time_total`` 、内存差 ``memory_total`` 。

        将以上四个变量传入 ``fmt`` 模板中格式化后输出到 ``log`` 。
        除上述变量外，您还可以使用装饰器参数中指定的变量。

        注意仅当 ``memory`` 为真时，才会记录日志情况，否则将直接跳过。

        日志输出模板中可使用变量如下:

        #. ``idx`` : 当前打点的序号，从 *1* 开始
        #. ``time_diff`` : 距上次打点间的时间差
        #. ``time_total`` : 距函数/方法开始时的时间差
        #. ``memory_diff`` : 距上次打点(memory=True)间的内存差，跳过未记录内存的时间打点，直到函数/方法进入时的内存记录
        #. ``memory_total`` : 距函数/方法开始时的内存差

        :param str fmt: 用来输出打点日志的格式化模板，需使用 format 的占位符格式
        :param int logging_level: 日志输出级别，默认使用装饰当前方法时设置的级别，若无则使用类属性中定义的默认值
        :param bool memory: 是否记录内存使用，默认为 False
        :param bool mute: 静默打点，默认为 False ，若设为 True ，则当次仅记录时间/内存，不执行任何输出逻辑
        """
        self.time_buf.append(time.time())
        if memory:
            self.mem_buf.append(self._get_mem_info())
        if mute:
            return

        idx = len(self.time_buf) - 1
        _fmt = fmt or (self.DOTTING_FMT_WITH_MEM_DEFAULT if memory else self.DOTTING_FMT_DEFAULT)
        _level = logging_level or self.logging_level
        kwargs.update(self.dkwargs)

        self.logger.log(_level, _fmt.format(
            time_diff=self.time_buf[-1] - self.time_buf[-2],
            time_total=self.time_buf[-1] - self.time_buf[0],
            mem_diff=(self.mem_buf[-1] - self.mem_buf[-2]) if memory else None,
            mem_total=(self.mem_buf[-1] - self.mem_buf[0]) if memory else None,
            idx=idx,
            **kwargs))


class StopwatchMixin(base.ProfilerMixin):
    """
    秒表 Mixin 类

    用以提供复杂的秒表功能，如:

    #. 针对需要多次调用的方法进行累加记录的场景
    #. 在一次代码执行流程中同时记录多个方法，并灵活控制记录结果的输出
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


def stopwatch(
        _function=None, print_args=False, logger=None, print_mem=False,
        fmt='', name='', logging_level=logging.INFO, **dkwargs):
    """
    返回秒表监控下的函数或方法

    通过额外的关键字参数，支持配置自定义的值到输出模板中

    日志输出模板中可使用变量如下:

    #. ``name`` : 当前秒表名称
    #. ``args`` : 被装饰函数/方法的位置参数
    #. ``kwargs`` : 被装饰函数/方法
    #. ``time_use`` : 函数/方法执行耗时
    #. ``mem_use`` : 函数/方法执行内存

    :param _function: 被封装的对象，由解释器自动传入，不需关心
    :type _function: types.FunctionType or types.MethodType
    :param bool print_args: 是否打印被装饰函数的参数列表，若含有较长的参数，可能造成日志过长，开启时请注意
    :param logging.Logger logger: 可传入指定的日志对象，便于统一输出样式，默认使用该模块中的全局 logger
    :param bool print_mem: 是否在方法退出时打印内存信息，默认为 False
    :param str fmt: 用于格式化输出的模板，可在了解所有内置参数变量后自行定制输出样式，若指定该参数则会忽略 print_args
    :param str name: 关键字参数，被装饰方法代理生成的 stopwatch 所使用的名称，默认为使用被装饰方法的方法名
    :param int logging_level: 打印日志的级别，默认为 INFO
    :return: 装饰后的函数
    :rtype: types.FunctionType or types.MethodType
    """
    invoked = bool(_function and callable(_function))
    if invoked:
        func = _function  # type: types.FunctionType or types.MethodType
    wrap_param = {
        'print_args': print_args,
        'logger': logger,
        'fmt': fmt,
        'name': name,
        'logging_level': logging_level,
        'dkwargs': dkwargs,
        'print_mem': print_mem,
    }

    def wrapper(func):
        """
        装饰器封装函数
        """
        @wraps(func)
        def inner(*args, **kwargs):
            """
            使用秒表封装被装饰对象

            若被封装方法的首个位置参数继承了 StopwatchMixin 则将被封装方法所用的
            self_or_cls 进行代理，从而在方法内可以访问到被代理的 stopwatch 属性

            若被封装方法的首个位置参数未继承 StopwatchMixin 则作为普通函数处理

            :param list args: 位置参数
            """
            if not (args and base.is_instance_or_subclass(args[0], StopwatchMixin)):
                # 若当前被装饰的方法未继承 StopwatchMixin ，则将其作为普通函数装饰
                _stopwatch_wrapper = Stopwatch()(func, wrap_param)
                return _stopwatch_wrapper(*args, **kwargs)

            self_or_cls = args[0]  # type: StopwatchMixin
            callargs = base.get_callargs(func, *args, **kwargs)
            callargs.pop("cls", None)
            with self_or_cls._get_stopwatch(self_or_cls, **callargs) as _self_or_cls:
                _stopwatch_wrapper = _self_or_cls.stopwatch(func, wrap_param)
                return _stopwatch_wrapper(_self_or_cls, *args[1:], **kwargs)
        return inner
    return wrapper if not invoked else wrapper(func)
