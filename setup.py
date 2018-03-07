#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
]

setup_requirements = [
    # (distutils extensions, etc.)
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='sessionlib',
    version='0.1.9',
    description="Session Library",
    long_description=readme + '\n\n' + history,
    author="Paulo Romeira",
    author_email='paulo@pauloromeira.com',
    url='https://github.com/pauloromeira/sessionlib',
    download_url='https://github.com/pauloromeira/sessionlib/tarball/0.1.9',
    packages=find_packages(include=['sessionlib']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='sessionlib',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # TODO [romeira]: Add support for 2.x python versions {04/12/17 09:29}
        # "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
