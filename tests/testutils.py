#!/usr/bin/python
# -*- coding: utf-8 -*-

# see  http://docs.python-guide.org/en/latest/writing/structure/
import os
import sys
import json
import unittest
# set path to sources
sys.path.insert(0, os.path.abspath('..'))


def jsonDefault(o):
    return o.__dict__


def ObjAsJson(o):
    return json.dumps(o, sort_keys=True, indent=2, separators=(',', ': '),
                      default=jsonDefault)


def assertEqualObjects(expected, actual):
    '''
    Assests if objects are equal by content when presented as JSON.
    Converts each object to JSON string and compares them.

    Example of code:
    class TestObj(object):
       def __init__(self, a, b):
          self.a = a
          self.b = b

    assertEqualObjects(TestObj(1,2), TestObj(1,2))
    '''
    expJson = ObjAsJson(expected)
    actJson = ObjAsJson(actual)
    t = unittest.TestCase('__init__')
    t.assertEqual(expJson, actJson)
