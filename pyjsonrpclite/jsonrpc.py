#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

class JsonRpcException(Exception):
   """Base class for exceptions in this module."""
   pass 
    

def defaultJsonEncode(o):
    return o.__dict__ 
            
    
class JsonRpcMessage(object):

    @classmethod
    def Request(cls, id, method, params):
        return JsonRpcRequestObject(id, method, params)

    @classmethod
    def Notification(cls, method, params = None):
        return JsonRpcNotificationObject(method, params)

    @classmethod
    def Success(cls, id, result):
        return JsonRpcSuccessObject(id, result)
    
    @classmethod
    def Error(cls, id, errorobj):
        return JsonRpcErrorObject(id, errorobj)


    def AsJson(self, indent = False, escape = True):
        return json.dumps(self, sort_keys=True, indent=indent,
            separators=(',', ': '), default=defaultJsonEncode)


class JsonRpcRequestObject(JsonRpcMessage):
    '''JSON-RPC 2.0 Request object'''
    def __init__(self, id, method, params = None): 
        self.id = id
        self.method = method
        self.params = params


class JsonRpcNotificationObject(JsonRpcRequestObject):
    '''JSON-RPC 2.0 Notification object'''
    def __init__(self, method, params = None):
        JsonRpcRequestObject.__init__(self, None, method, params)
        

class JsonRpcSuccessObject(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request success'''
    def __init__(self, id, result):
        self.id = id
        self.result = result


class JsonRpcErrorObject(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request error. 
    Contains JsonRpcError object'''
    def __init__(self, id, errorobj):
        self.id = id
        self.error = errorobj


class JsonRpcParsedType(object):
    '''Types used by parser to identify parsedType result in JsonRpcParsed'''
    INVALID = 'INVALID'
    REQUEST = 'REQUEST'
    NOTIFICATION = 'NOTIFICATION'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'


class JsonRpcParsed(object):
    '''Presents a json string parse result: parsedType and payload'''
    def __init__(self, parsedType, payload):
        self.parsedType = parsedType
        self.payload = payload 

    @classmethod
    def Parse(jsonstr):
        '''Parses json formatted string. 
        Returns JsonRpcParsed object containing Parse results.''' 
        
        def SubCheckHeader(jsonobj):        
            '''Parses header and validate values.
            Returns True or raises JsonRpcException in case of error'''
            if not hasattr(jsonobj, 'jsonrpc'):
                raise JsonRpcException('Message have no "jsonrpc" field')
            if jsonobj.jsonrpc <> '2.0':                                    
                raise JsonRpcException('"jsonrpc" field value should be 2.0')
            return True 
        
        def SubHasId(jsonobj):
            return hasattr(jsonobj, 'id')       
            
        def SubHasValidId(jsonobj):
            '''Checks if Id message field present and has valid value'''
            isIdValid = SubHasId(jsonobj) and (not jsonobj.id is None) \
                and (jsonobj.id <> '') 
            return isIdValid   
            
        def SubHasMethod(jsonobj):
            return hasattr(jsonobj, 'method') 

        def SubIsMethodValid(jsonobj):
            '''Checks if "method" message field has valid value.
            Returns boolean'''
            methodValid = SubHasMethod and (not jsonobj.method is None) \
                and len(jsonobj.method) > 0
            return methodValid  
        
        def SubValidateMethod(jsonobj):
            if not SubHasMethod(jsonobj):
                raise JsonRpcException('No "method" field')
            if not SubIsMethodValid(jsonobj):
                raise JsonRpcException('Invalid "method" field value')              
        
        def SubParseJsonRpcObject(jsonobj):
            '''Check if jsonobj is valid JSON-RPC 2.0 object.
            Returns JsonRpcParsed object containing Parse results.'''
            try:
                SubCheckHeader(jsonobj)
            except JsonRpcException as e:
                return JsonRpcParsed(JsonRpcParsedType.INVALID, 
                    JsonRpcError.InvalidRequest(e))
            
            isNotification = not SubHasValidId(jsonobj)  
            if isNotification:                      
                try:
                    SubValidateMethod(jsonobj)  
                    data = JsonRpcMessage.Notification(jsonobj.method, jsonobj.params)
                    return JsonRpcParsed(JsonRpcParsedType.NOTIFICATION, data)
                except JsonRpcException as e:                    
                    return JsonRpcParsed(JsonRpcParsedType.INVALID, 
                        JsonRpcError.InvalidRequest(e))
            #else it has Id so it may be: request, success, error message
            isRequest = SubIsMethodValid(jsonobj)
            if isRequest:
                data = JsonRpcMessage.Request(jsonobj.id, jsonobj.method, 
                    jsonobj.params)
                return JsonRpcParsed(JsonRpcParsedType.REQUEST, data)     
            # no METHOD field so it may be: success, error message  
            
            isResultMsg = hasattr(jsonobj, 'result')
            if isResultMsg:
                data = JsonRpcMessage.Success(jsonobj.id, jsonobj.result)
                return JsonRpcParsed(JsonRpcParsedType.SUCCESS, data)  
                
            isErrorMsg = hasattr(jsonobj, 'error')
            if isErrorMsg:           
                err = jsonobj.error                                     
                errorobj = JsonRpcErrorObject(err.code, err.message, err.data) 
                data = JsonRpcMessage.Error(jsonobj.id, errorobj)
                return JsonRpcParsed(JsonRpcParsedType.ERROR, data) 
            # no result, no error - id only             
            return JsonRpcParsed(JsonRpcParsedType.INVALID, 
                        JsonRpcError.InvalidRequest())
        try:
            jsonObj = json.loads(jsonstr) 
            return SubParseJsonRpcObject(jsonObj)
        except ValueError as e:
            errorobj = JsonRpcErrorObject(JsonRpcError.ParseError(jsonstr))
            return JsonRpcParsed(JsonRpcParsedType.INVALID, errorobj)
        except Exception as e:   
            errorobj = JsonRpcErrorObject(JsonRpcError.InternalError(e))
            return JsonRpcParsed(JsonRpcParsedType.INVALID, errorobj)


class JsonRpcError(object):
    '''Class implements JSON-RPC 2.0 Error Object'''
    
    def __init__(self, code, message, data = None):
        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def Error(cls, code, message, data = None):
        return JsonRpcError(code, message, data)

    @classmethod
    def ParseError(cls, code, message, data = None):
        code = -32700
        message = 'Parse Error'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidRequest(cls, code, message, data = None):
        code = -32600
        message = 'Invalid Request'
        return JsonRpcError(code, message, data)

    @classmethod
    def MethodNotFound(cls, code, message, data = None):
        code = -32601
        message = 'Method Not Found'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidParams(cls, code, message, data = None):
        code = -32602
        message = 'Invalid Params'
        return JsonRpcError(code, message, data)

    @classmethod
    def InternalError(cls, data = None):   
        code = -32603
        message = 'Internal Error'
        return JsonRpcError(code, message, data)
        
#TODO: Batch request/response object ??