py-jsonrpc-lite
===============

.. image:: https://travis-ci.org/r3code/py-jsonrpc-lite.svg?branch=master
    :target: https://travis-ci.org/r3code/py-jsonrpc-lite
    :alt: Build Status

.. image:: https://codecov.io/gh/r3code/py-jsonrpc-lite/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/r3code/py-jsonrpc-lite
    :alt: Coverage Status 
    
.. image:: https://api.codacy.com/project/badge/Grade/acf5dba2b46242a1a85d171f884f3993
    :target: https://www.codacy.com/app/r3code/py-jsonrpc-lite  
    :alt: Code Quality Status

Inspired by https://www.npmjs.com/package/jsonrpc-lite

A implementation of py-jsonrpc-lite 2.0 specifications <http://www.jsonrpc.org/specification>

This implementation does not have any transport functionality realization, only protocol.

#todo: Documentation: http://py-jsonrpc-lite.readthedocs.org

Install
-------

pip install py-jsonrpc-lite

Tests
-----

python -m unittest discover -s "tests" -p "test*.py"

Features
--------

- Vanilla python, no dependencies
- py-jsonrpc-lite 2.0 support

Testing
-------
py-jsonrpc-lite is a python library, it supports pythons:  2.7. 