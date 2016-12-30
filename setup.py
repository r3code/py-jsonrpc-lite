#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from pyjsonrpclite import version


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ""


setup(
    name="py-jsonrpc-lite",
    version=version,
    packages=find_packages(),
    test_suite="nose.collector",
    tests_require=["nose", "mock"],

    # metadata for upload to PyPI
    author="Dmitriy S. Sinyavskiy",
    author_email="contact@r3code.ru",
    url="https://github.com/r3code/py-jsonrpc-lite",
    description="Parse and Serialize JSON-RPC 2.0 messages in Python",
    long_description=read('README.rst'),

    # Full list:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
)
