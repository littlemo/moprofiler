# encoding=utf8
from __future__ import unicode_literals

from setuptools import find_packages, setup

VERSION_SUFFIX_DEV = 'dev'
VERSION_SUFFIX_POST = 'post'
VERSION_SUFFIX_ALPHA = 'a'
VERSION_SUFFIX_BETA = 'b'
VERSION_SUFFIX_RC = 'rc'
VERSION_SUFFIX_NONE = None

VERSION = (1, 0, 0, VERSION_SUFFIX_NONE, 0)


def get_setup_version():
    """
    获取打包使用的版本号，符合 PYPI 官方推荐的版本号方案

    :return: PYPI 打包版本号
    :rtype: str
    """
    ver = '.'.join(map(str, VERSION[:3]))

    # 若后缀描述字串为 None ，则直接返回主版本号
    if not VERSION[3]:
        return ver

    # 否则，追加版本号后缀
    hyphen = ''
    suffix = hyphen.join(map(str, VERSION[-2:]))
    if VERSION[3] in [VERSION_SUFFIX_DEV, VERSION_SUFFIX_POST]:
        hyphen = '.'
    ver = hyphen.join([ver, suffix])

    return ver


setup(
    name='moprofiler',
    url='https://github.com/littlemo/moprofiler',
    author='littlemo',
    author_email='moore@moorehy.com',
    maintainer='littlemo',
    maintainer_email='moore@moorehy.com',
    version=get_setup_version(),
    description='综合性能分析工具，集成了内存使用、执行时间的分析器，及秒表打点工具',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='moprofiler profiler tool memory time',
    packages=find_packages('source'),
    package_dir={'': 'source'},
    include_package_data=True,
    zip_safe=False,
    license='GPLv3',
    python_requires='>=2.7',
    project_urls={
        'Documentation': 'http://moprofiler.rtfd.io/',
        'Source': 'https://github.com/littlemo/moprofiler',
        'Tracker': 'https://github.com/littlemo/moprofiler/issues',
    },
    install_requires=open('requirements/pip.txt').read().splitlines(),
    entry_points={},

    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Email',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development :: Testing :: Unit',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Version Control :: Git',
        'Topic :: Terminals',
        'Topic :: Text Editors :: Emacs',
        'Topic :: Utilities',
    ],
)
