﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import unittest
import testutils

from pyjsonrpclite import JsonRpcMessage, JsonRpcRequest, JsonRpcNotification,\
    JsonRpcSuccessResponse, JsonRpcErrorResponse,\
    JsonRpcError, JsonRpcParsedType, JsonRpcParsed,\
    JsonRpcParseError

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('..\..'))


class TestJsonRpc(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # pylint: disable=R0201
    def testJsonRpcMessageRequestCorrect(self):
        expected = JsonRpcRequest(1, 'login', ['user', 'password'])
        actual = JsonRpcMessage.Request(1, 'login', ['user', 'password'])
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageRequestNoParamsCorrect(self):
        expected = JsonRpcRequest(1, 'login')
        actual = JsonRpcMessage.Request(1, 'log0in')
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageNotificationCorrect(self):
        expected = JsonRpcNotification('alarm', ['a', 'b'])
        actual = JsonRpcMessage.Notification('alarm', ['a', 'b'])
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageNotificationNoParamsCorrect(self):
        expected = JsonRpcNotification('alarm')
        actual = JsonRpcMessage.Notification('alarm')
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageSuccessCorrect(self):
        expected = JsonRpcSuccessResponse(1, 1107)
        actual = JsonRpcMessage.Success(1, 1107)
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageErrorCorrect(self):
        expected = JsonRpcErrorResponse(
            1, JsonRpcError(-32001, 'Err MSG', [105, 106]))
        actual = JsonRpcMessage.Error(
            1, JsonRpcError(-32001, 'Err MSG', [105, 106]))
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcMessageAsJsonCorrect(self):
        # request
        expected = '{\n"id": 1,\n"method": "login",' +\
            '\n"params": [\n"user",\n"password"\n]\n}'
        msg = JsonRpcMessage.Request(1, 'login', ['user', 'password'])
        actual = JsonRpcMessage.AsJson(msg, indent=False, escape=True)
        self.assertEqual(expected, actual)

        # request, no params
        expected = '{\n"id": 1,\n"method": "login"\n}'
        msg = JsonRpcMessage.Request(1, 'login')
        actual = JsonRpcMessage.AsJson(msg, indent=False, escape=True)
        self.assertEqual(expected, actual)

        # notify
        expected = '{\n"method": "alarm",\n"params": [\n"a",\n"b"\n]\n}'
        msg = JsonRpcMessage.Notification('alarm', ['a', 'b'])
        actual = JsonRpcMessage.AsJson(msg, indent=False, escape=True)
        self.assertEqual(expected, actual)

        # notify, no params
        expected = '{\n"method": "alarm"\n}'
        msg = JsonRpcMessage.Notification('alarm')
        actual = JsonRpcMessage.AsJson(msg, indent=False, escape=True)
        self.assertEqual(expected, actual)

    # pylint: disable=R0201
    def testJsonRpcRequestCorrect(self):
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcRequest(1, 'methodName', 'params')
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'method'))
        self.assertTrue(hasattr(msg, 'params'))
        self.assertEqual(1, msg.id)
        self.assertEqual('methodName', msg.method)
        self.assertEqual('params', msg.params)

    # pylint: disable=R0201
    def testJsonRpcNotificationCorrect(self):
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcNotification('ntfName', 'params')
        self.assertTrue(isinstance(msg, JsonRpcRequest))
        self.assertFalse(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'method'))
        self.assertTrue(hasattr(msg, 'params'))
        self.assertEqual('ntfName', msg.method)
        self.assertEqual('params', msg.params)

    # pylint: disable=R0201
    def testJsonRpcSuccessResponseCorrect(self):
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcSuccessResponse(1, 'result-value')
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'result'))
        self.assertEqual(1, msg.id)
        self.assertEqual('result-value', msg.result)

    # pylint: disable=R0201
    def testJsonRpcErrorResponseCorrect(self):
        '''Checks object inheritance, structure, init'''
        msg = JsonRpcErrorResponse(
            1, JsonRpcError(-32000, 'TestError', 'Error-data'))
        self.assertTrue(isinstance(msg, JsonRpcMessage))
        self.assertTrue(hasattr(msg, 'id'))
        self.assertTrue(hasattr(msg, 'error'))
        self.assertTrue(isinstance(msg.error, JsonRpcError))
        self.assertEqual(1, msg.id)
        self.assertEqual(msg.error.code, -32000)
        self.assertEqual(msg.error.message, 'TestError')
        self.assertEqual(msg.error.data, 'Error-data')

    # pylint: disable=R0201
    def testInternalErrorCorrect1(self):
        msg = JsonRpcError.InternalError('Error-data')
        self.assertTrue(isinstance(msg, JsonRpcError))
        self.assertTrue(hasattr(msg, 'code'))
        self.assertTrue(hasattr(msg, 'message'))
        self.assertTrue(hasattr(msg, 'data'))
        self.assertEqual(-32603, msg.code)
        self.assertEqual('Internal Error', msg.message)
        self.assertEqual('Error-data', msg.data)

    # pylint: disable=R0201
    def testInternalErrorCorrect2(self):
        msg = JsonRpcError.InternalError()
        self.assertTrue(isinstance(msg, JsonRpcError))
        self.assertTrue(hasattr(msg, 'code'))
        self.assertTrue(hasattr(msg, 'message'))
        self.assertEqual(-32603, msg.code)
        self.assertEqual('Internal Error', msg.message)

    # pylint: disable=R0201
    def testCustomErrorCorrect1(self):
        msg = JsonRpcError.Error(-32099, 'tes-msg', 'Error-data')
        self.assertTrue(isinstance(msg, JsonRpcError))
        self.assertTrue(hasattr(msg, 'code'))
        self.assertTrue(hasattr(msg, 'message'))
        self.assertTrue(hasattr(msg, 'data'))
        self.assertEqual(-32099, msg.code)
        self.assertEqual('tes-msg', msg.message)
        self.assertEqual('Error-data', msg.data)

    # pylint: disable=R0201
    def testCustomErrorCorrect2(self):
        msg = JsonRpcError.Error(-32099, 'tes-msg')
        self.assertTrue(isinstance(msg, JsonRpcError))
        self.assertTrue(hasattr(msg, 'code'))
        self.assertTrue(hasattr(msg, 'message'))
        self.assertEqual(-32099, msg.code)
        self.assertEqual('tes-msg', msg.message)

    # pylint: disable=R0201
    def testParseRequest(self):
        '''Checks if JSON-RPC 2.0 Request object parsed correct'''
        testReqJson = '''
        {
            "jsonrpc": "2.0",
            "method": "sum",
            "params": {"param1": 1, "param2": 2},
            "id": 521
        }'''
        expected = JsonRpcParsed(
            JsonRpcParsedType.REQUEST,
            JsonRpcRequest(521, 'sum', {"param1": 1, "param2": 2})
        )
        actual = JsonRpcParsed.Parse(testReqJson)
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testParseRequestInvalidRaisesException(self):
        '''Parse json with "id" only raises JsonRpcParseError'''
        testReqJson = '''
        {
            "jsonrpc": "2.0",
            "id": 521
        }'''
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest('No reqired fields')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseNotificationReq(self):
        '''Checks if JSON-RPC 2.0 Notification object parsed correct'''
        testReqJson = '''
        {
            "jsonrpc": "2.0",
            "method": "alarmAdd",
            "params": {"param1": 1, "param2": 2}
        }'''
        expected = JsonRpcParsed(
            JsonRpcParsedType.NOTIFICATION,
            JsonRpcNotification('alarmAdd', {"param1": 1, "param2": 2})
        )
        actual = JsonRpcParsed.Parse(testReqJson)
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testParseSuccessRes(self):
        '''Checks if JSON-RPC 2.0 Success object parsed correct'''
        testReqJson = '''
        {
            "jsonrpc": "2.0",
            "result": 3,
            "id": 521
        }'''
        expected = JsonRpcParsed(
            JsonRpcParsedType.SUCCESS,
            JsonRpcSuccessResponse(521, 3)
        )
        actual = JsonRpcParsed.Parse(testReqJson)
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testParseErrorObj1(self):
        '''Checks if JSON-RPC 2.0 Error object parsed correct'''
        testReqJson = '''
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": "Method Not Found",
                "data": "No method called [sum]"
            },
            "id": 521
        }'''
        rpcerror = JsonRpcError.MethodNotFound('No method called [sum]')
        expected = JsonRpcParsed(
            JsonRpcParsedType.ERROR,
            JsonRpcErrorResponse(521, rpcerror)
            )
        actual = JsonRpcParsed.Parse(testReqJson)
        testutils.assertEqualObjects(expected, actual)

    # pylint: disable=R0201
    def testParseErrorObjInvalidCode1(self):
        '''Parse JSON-RPC 2.0 Error object with invalid code raises
        exception.'''
        def SubGetErrornousErrObj(code):
            return '''
        {
            "jsonrpc": "2.0",
            "error": {
                "code": ''' + str(code) + ''',
                "message": "Method Not Found",
                "data": "No method called [sum]"
            },
            "id": 521
        }'''
        testReqJson = SubGetErrornousErrObj(-32800)
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error code')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

        testReqJson = SubGetErrornousErrObj(-32604)
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error code')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

        testReqJson = SubGetErrornousErrObj(-32599)
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error code')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

        testReqJson = SubGetErrornousErrObj(-32100)
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error code')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

        testReqJson = SubGetErrornousErrObj(-31199)
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error code')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseReturnsParseError(self):
        '''Parse found invalid json'''
        testReqJson = """{INVALID_JSON}"""
        with self.assertRaises(JsonRpcParseError) as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.ParseError('{INVALID_JSON}')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidHeader1(self):
        '''Parse found JSON-PRC message without jsonrpc field'''

        testReqJson = '''{

            "error": {
                "code": -32601,
                "message": "Method Not Found",
                "data": "No method called [sum]"
            },
            "id": 521
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest(
            'Message have no "jsonrpc" field')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidHeader2(self):
        '''Parse found JSON-PRC message jsonrpc wrong version'''

        testReqJson = '''{
            "jsonrpc": "1.0",
            "error": {
                "code": -32601,
                "message": "Method Not Found",
                "data": "No method called [sum]"
            },
            "id": 521
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest(
            '"jsonrpc" field value should be 2.0')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidNotifyReq1(self):
        '''Parse found JSON-PRC 2.0 Notify Request without method field'''

        testReqJson = '''{
            "jsonrpc": "2.0"
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest('No "method" field')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidNotifyReq2(self):
        '''Parse found JSON-PRC 2.0 Notify Request where method is null'''

        testReqJson = '''{
            "jsonrpc": "2.0",
            "method": null
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest(
            'Invalid "method" field value')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidNotifyReq3(self):
        '''Parse found JSON-PRC 2.0 Notify Request where method is empty'''

        testReqJson = '''{
            "jsonrpc": "2.0",
            "method": ""
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidRequest(
            'Invalid "method" field value')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)

    # pylint: disable=R0201
    def testParseInvalidErrorRes1(self):
        '''Parse found JSON-PRC 2.0 Response Error where error object has
        invalid structure.'''
        testReqJson = '''{
            "jsonrpc": "2.0",
            "error": "",
            "id": 536
        }'''
        with self.assertRaises(JsonRpcParseError)as context:
            JsonRpcParsed.Parse(testReqJson)
        expectedErr = JsonRpcError.InvalidParams(
            'Invalid JSON-RPC 2.0 Error object structure')
        testutils.assertEqualObjects(expectedErr, context.exception.rpcError)


if __name__ == '__main__':
    unittest.main()
