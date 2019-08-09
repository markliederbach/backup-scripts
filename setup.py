#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools.command.test import test

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

import os
import sys

from backup_scripts import __version__

with open('README.md') as readme_file:
    readme = readme_file.read()


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


base_dir = os.path.dirname(__file__)
requirements_dir = os.path.join(base_dir, 'requirements')
base_reqs = parse_requirements(os.path.join(requirements_dir, 'base.txt'), session=False)
requirements = [str(br.req) for br in base_reqs]
dev_reqs = parse_requirements(os.path.join(requirements_dir, 'dev.txt'), session=False)
test_requirements = [str(dr.req) for dr in dev_reqs]

setup(
    name='backup_scripts',
    version=__version__,
    description="Scripts to backup system resources",
    long_description=readme,
    author="Mark Liederbach",
    author_email='backup-scripts@northmail.net',
    url='https://github.com/markliederbach/backup-scripts',
    packages=[
        'backup_scripts',
    ],
    package_dir={'backup_scripts':
                 'backup_scripts'},
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'backup-nextcloud-s3=backup_scripts.main:main',
        ],
    },
    license="MIT",
    zip_safe=False,
    keywords='backup_scripts',
    classifiers=[
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
