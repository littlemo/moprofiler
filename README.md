# MoProfiler

综合性能分析工具，集成了内存使用、执行时间的分析器，及秒表打点工具

## Badge

### GitHub

[![GitHub followers](https://img.shields.io/github/followers/littlemo.svg?label=github%20follow)](https://github.com/littlemo)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/littlemo/moprofiler.svg)](https://github.com/littlemo/moprofiler)
[![GitHub stars](https://img.shields.io/github/stars/littlemo/moprofiler.svg?label=github%20stars)](https://github.com/littlemo/moprofiler)
[![GitHub release](https://img.shields.io/github/release/littlemo/moprofiler.svg)](https://github.com/littlemo/moprofiler/releases)
[![Github commits (since latest release)](https://img.shields.io/github/commits-since/littlemo/moprofiler/latest.svg)](https://github.com/littlemo/moprofiler)

[![Github All Releases](https://img.shields.io/github/downloads/littlemo/moprofiler/total.svg)](https://github.com/littlemo/moprofiler/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/littlemo/moprofiler.svg)](https://github.com/littlemo/moprofiler/releases)

### CI

[![Build Status](https://travis-ci.org/littlemo/moprofiler.svg?branch=master)](https://travis-ci.org/littlemo/moprofiler)
[![Documentation Status](https://readthedocs.org/projects/moprofiler/badge/?version=latest)](http://moprofiler.readthedocs.io/zh_CN/latest/?badge=latest)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=alert_status)](https://sonarcloud.io/dashboard?id=littlemo_moprofiler)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=coverage)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Coverage)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=ncloc)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=ncloc)

[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=sqale_rating)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Maintainability)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=reliability_rating)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Reliability)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=security_rating)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Security)

[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=vulnerabilities)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Security)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=bugs)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Reliability)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=duplicated_lines_density)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Duplications)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=code_smells)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Maintainability)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=littlemo_moprofiler&metric=sqale_index)](https://sonarcloud.io/component_measures?id=littlemo_moprofiler&metric=Maintainability)

### PyPi

[![PyPI](https://img.shields.io/pypi/v/moprofiler.svg)](https://pypi.org/project/moprofiler/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/moprofiler.svg)](https://pypi.org/project/moprofiler/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/moprofiler.svg)](https://pypi.org/project/moprofiler/)
[![PyPI - Format](https://img.shields.io/pypi/format/moprofiler.svg)](https://pypi.org/project/moprofiler/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/moprofiler.svg)](https://pypi.org/project/moprofiler/)
[![PyPI - Status](https://img.shields.io/pypi/status/moprofiler.svg)](https://pypi.org/project/moprofiler/)

### 其他

[![license](https://img.shields.io/github/license/littlemo/moprofiler.svg)](https://github.com/littlemo/moprofiler)
[![](https://img.shields.io/badge/bitcoin-donate-green.svg)](https://keybase.io/littlemo)

## 项目描述

了解更多，可查看 [官方文档](http://moprofiler.rtfd.io)

## 特性

1. 提供了对 [line_profiler](https://github.com/rkern/line_profiler) 时间分析器的封装，便于在被装饰函数外打印分析结果
2. 提供了对 [memory-profiler](https://github.com/pythonprofilers/memory_profiler) 内存分析器的封装，便于在被装饰函数外打印分析结果
3. 提供了用于打点计时的秒表工具，方便记录函数的关键执行节点，以及局部切片代码的执行耗时，可用于生产场景
4. 上述三个工具提供了对外统一的 *装饰器* 与 *Mixin* 使用方式
5. 兼容 `Python2` 与 `Python3`

## License

本项目采用 [![license](https://img.shields.io/github/license/littlemo/moprofiler.svg)](https://github.com/littlemo/moprofiler) 协议开源发布，请您在修改后维持开源发布，并为原作者额外署名，谢谢您的尊重。

若您需要将本项目应用于商业目的，请单独联系本人( [@littlemo](https://github.com/littlemo) )，获取商业授权。

## 问题

如果您在使用该应用时遇到任何问题，请在 GitHub 上查看本项目 [![moprofiler](https://img.shields.io/badge/Repo-Moprofiler-brightgreen.svg)](https://github.com/littlemo/moprofiler) ，并在其中提交 [Issues](https://github.com/littlemo/moprofiler/issues) 给我，多谢您的帮助~~

## 捐赠

来杯咖啡可好~~ **⁄(⁄ ⁄•⁄ω⁄•⁄ ⁄)⁄**

![支付宝](https://github.com/littlemo/moear/blob/master/docs/source/intro/images/donate/alipay.png "来杯咖啡可好~")
