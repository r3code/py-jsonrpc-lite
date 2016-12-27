#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('..\..'))

import unittest

from pyjsonrpclite import *  

import json
from datetime import datetime
from shutil import copyfile
import testutils 

            
  
class TestJsonRpc(unittest.TestCase):
   
    def setUp(self):
        pass  
   
    def tearDown(self):
        pass 
   
    def testJsonRpcMessageRequestCorrect(self):     
        expected = JsonRpcRequestObject(1, 'login', ['user', 'password'])
        actual = JsonRpcMessage.Request(1, 'login', ['user', 'password'])
        testutils.assertEqualObjects(expected, actual) 
   
    def testJsonRpcMessageNotificationCorrect(self):     
        expected = JsonRpcNotificationObject('alarm', ['a','b'])
        actual = JsonRpcMessage.Notification('alarm', ['a','b'])
        testutils.assertEqualObjects(expected, actual) 
   
    def testJsonRpcMessageSuccessCorrect(self):     
        expected = JsonRpcSuccessObject(1, 1107)
        actual = JsonRpcMessage.Success(1, 1107)
        testutils.assertEqualObjects(expected, actual) 
   
    def testJsonRpcMessageErrorCorrect(self):     
        expected = JsonRpcErrorObject(1, JsonRpcError(-32001, 'Err MSG', [105, 106]))
        actual = JsonRpcMessage.Error(1, JsonRpcError(-32001, 'Err MSG', [105, 106]))
        testutils.assertEqualObjects(expected, actual)
        
    def testJsonRpcMessageAsJsonCorrect(self):     
        expected = '{\n"id": 1,\n"method": "login",\n"params": [\n"user",\n"password"\n]\n}'
 
        msg = JsonRpcMessage.Request(1, 'login', ['user', 'password'])
        actual = JsonRpcMessage.AsJson(msg, indent=False, escape=True)  
        self.assertEqual(expected, actual) 
        
    def testJsonRpcRequestObjectCorrect(self):    
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcRequestObject(1, 'methodName', 'params')  
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'method'))
        self.assertTrue(hasattr(msg, 'params'))
        self.assertEqual(1, msg.id)
        self.assertEqual('methodName', msg.method)
        self.assertEqual('params', msg.params) 
        
    def testJsonRpcNotificationObjectCorrect(self): 
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcNotificationObject('ntfName', 'params')  
        self.assertTrue(isinstance(msg, JsonRpcRequestObject))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'method'))
        self.assertTrue(hasattr(msg, 'params'))
        self.assertEqual(None, msg.id)
        self.assertEqual('ntfName', msg.method)
        self.assertEqual('params', msg.params)
        
    def testJsonRpcSuccessObjectCorrect(self):      
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcSuccessObject(1, 'result-value')  
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'result'))
        self.assertEqual(1, msg.id)
        self.assertEqual('result-value', msg.result)
        
    def testJsonRpcErrorObjectCorrect(self):      
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcErrorObject(1, JsonRpcError(-32000, 'TestError', 'Error-data'))  
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'error')) 
        self.assertTrue(isinstance(msg.error, JsonRpcError))
        self.assertEqual(1, msg.id)
        self.assertEqual(msg.error.code, -32000)
        self.assertEqual(msg.error.message, 'TestError')
        self.assertEqual(msg.error.data, 'Error-data')
        
        

if __name__ == '__main__':
    unittest.main()
