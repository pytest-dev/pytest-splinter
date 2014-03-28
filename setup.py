import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

dirname = os.path.dirname(__file__)

long_description = (
    open(os.path.join(dirname, 'README.rst')).read() + '\n' +
    open(os.path.join(dirname, 'CHANGES.rst')).read()
)


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--recreate']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import detox.main
        errno = detox.main.main(self.test_args)
        sys.exit(errno)


setup(
    name='pytest-splinter',
    description='Splinter subplugin for Pytest BDD plugin',
    long_description=long_description,
    author='Paylogic developers',
    license='MIT license',
    author_email='developers@paylogic.com',
    version='1.0.1',
    cmdclass={'test': Tox},
    url='https://github.com/paylogic/pytest-splinter',
    install_requires=[
        'setuptools',
        'splinter',
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
    ] + [('Programming Language :: Python :: %s' % x) for x in '2.6 2.7 3.0 3.1 3.2 3.3'.split()],
    tests_require=['detox'],
    entry_points={'pytest11': ['pytest-splinter=pytest_splinter.plugin']},
    packages=['pytest_splinter'],
)
