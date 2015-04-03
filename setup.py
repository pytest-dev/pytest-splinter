"""Setuptools entry point."""
import codecs
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import pytest_splinter

dirname = os.path.dirname(__file__)

long_description = (
    codecs.open(os.path.join(dirname, 'README.rst'), encoding='utf-8').read() + '\n' +
    codecs.open(os.path.join(dirname, 'AUTHORS.rst'), encoding='utf-8').read() + '\n' +
    codecs.open(os.path.join(dirname, 'CHANGES.rst'), encoding='utf-8').read()
)


class Tox(TestCommand):

    """Integrate tox runner to setuptools."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = "--recreate"

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)


setup(
    name='pytest-splinter',
    description='Splinter plugin for pytest testing framework',
    long_description=long_description,
    author='Anatoly Bubenkov, Paylogic International and others',
    license='MIT license',
    author_email='bubenkoff@gmail.com',
    version=pytest_splinter.__version__,
    cmdclass={'test': Tox},
    include_package_data=True,
    url='https://github.com/pytest-dev/pytest-splinter',
    install_requires=[
        'setuptools',
        'splinter>=0.7.2',
        'pytest',
    ],
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ] + [('Programming Language :: Python :: %s' % x) for x in '2.6 2.7 3.0 3.1 3.2 3.3 3.4'.split()],
    tests_require=['detox'],
    entry_points={'pytest11': [
        'pytest-splinter=pytest_splinter.plugin',
    ]},
    packages=['pytest_splinter'],
)
