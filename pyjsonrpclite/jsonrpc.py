#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

class JsonRpcException(Exception):
    """Base class for exceptions in this module."""
    pass
       
    
class JsonRpcParseError(Exception):
    """Raised if Parse JSON-RPC 2.0 string failed.
    Params:
        rpcError - JsonRpcError """  
    def __init__(self, rpcError):
        Exception.__init__(self, rpcError)         
        self.rpcError = rpcError         
                  
        
def defaultJsonEncode(o):
    return o.__dict__ 
            
    
class JsonRpcMessage(object):

    @classmethod
    def Request(cls, id, method, params):
        return JsonRpcRequest(id, method, params)

    @classmethod
    def Notification(cls, method, params = None):
        return JsonRpcNotification(method, params)

    @classmethod
    def Success(cls, id, result):
        return JsonRpcSuccessResponse(id, result)
    
    @classmethod
    def Error(cls, id, errorobj):
        return JsonRpcErrorResponse(id, errorobj)


    def AsJson(self, indent = False, escape = True):
        return json.dumps(self, sort_keys=True, indent=indent,
            separators=(',', ': '), default=defaultJsonEncode)


class JsonRpcRequest(JsonRpcMessage):
    '''JSON-RPC 2.0 Request object'''
    def __init__(self, id, method, params = None): 
        self.id = id
        self.method = method
        self.params = params


class JsonRpcNotification(JsonRpcRequest):
    '''JSON-RPC 2.0 Notification object'''
    def __init__(self, method, params = None):
        JsonRpcRequest.__init__(self, None, method, params)
        

class JsonRpcSuccessResponse(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request success'''
    def __init__(self, id, result):
        self.id = id
        self.result = result


class JsonRpcErrorResponse(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request error.
    Params:
        id -- errornous request id or None,
        err - JsonRpcError object with an error data 
    '''
    def __init__(self, id, err):
        self.id = id
        self.error = err


class JsonRpcParsedType(object):
    '''Types used by parser to identify parsedType result in JsonRpcParsed'''
    INVALID = 'INVALID'
    REQUEST = 'REQUEST'
    NOTIFICATION = 'NOTIFICATION'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'    
    

class JsonRpcParsed(object):
    '''Presents a json string parse result: parsedType and payload.
    Params:
        parsedType  -- JsonRpcParsedType,
        payload     -- JsonRpcMessage or JsonRpcError if parse failed'''
    def __init__(self, parsedType, payload):
        self.parsedType = parsedType
        self.payload = payload 

    @classmethod
    def Parse(cls, jsonstr):
        '''Parses json formatted string. 
        Raises JsonRpcParseError if Parse fails. 
        Return a JsonRpcParsed.'''
        
        def SubHasId(jsondict):
            return 'id' in jsondict       
            
        def SubHasValidId(jsondict):
            '''Checks if Id message field present and has valid value'''
            
            isIdValid = SubHasId(jsondict) and (not jsondict['id'] is None) \
                and (jsondict['id'] <> '') 
            return isIdValid   
            
        def SubHasMethod(jsondict):
            return 'method' in jsondict 

        def SubIsMethodCorrect(jsondict):
            '''Checks if "method" message field has valid value.
            Returns boolean'''
            methodValid = SubHasMethod(jsondict) and (not jsondict['method'] is None) \
                and len(jsondict['method']) > 0
            return methodValid  
        
        def SubValidateHeader(jsondict):        
            '''Parses header and validate values.
            Returns True or raises JsonRpcException in case of error'''
            if not 'jsonrpc' in jsondict:
                raise JsonRpcException('Message have no "jsonrpc" field')
            if jsondict['jsonrpc'] <> '2.0':                                    
                raise JsonRpcException('"jsonrpc" field value should be 2.0')
            return True 
        
        def SubValidateMethod(jsondict):
            if not SubHasMethod(jsondict):
                raise JsonRpcException('No "method" field')
            if not SubIsMethodCorrect(jsondict):
                raise JsonRpcException('Invalid "method" field value') 
            return True             
        
        def SubParseJsonRpcObject(jsondict):
            '''Check if jsondict is valid JSON-RPC 2.0 object.
            Returns JsonRpcParsed object containing Parse results.'''
            try:
                SubValidateHeader(jsondict)
            except JsonRpcException as e:
                raise JsonRpcParseError(JsonRpcError.InvalidRequest(str(e)))
            
            isNotification = not SubHasValidId(jsondict)  
            if isNotification:                      
                try:
                    SubValidateMethod(jsondict)  
                    data = JsonRpcMessage.Notification(jsondict['method'], \
                        jsondict['params'])
                    return JsonRpcParsed(JsonRpcParsedType.NOTIFICATION, data)
                except JsonRpcException as e:                    
                    raise JsonRpcParseError(JsonRpcError.InvalidRequest(str(e)))
            #else it has Id so it may be: request, success, error message
            isRequest = SubIsMethodCorrect(jsondict)
            if isRequest:
                data = JsonRpcMessage.Request(jsondict['id'], \
                    jsondict['method'], jsondict['params'])
                return JsonRpcParsed(JsonRpcParsedType.REQUEST, data)     
            # no METHOD field so it may be: success, error message  
            
            isSuccessMsg = 'result' in jsondict  
            if isSuccessMsg:
                data = JsonRpcMessage.Success(jsondict['id'], jsondict['result'])                 
                return JsonRpcParsed(JsonRpcParsedType.SUCCESS, data)  
                
            isErrorMsg = 'error' in jsondict
            if isErrorMsg:           
                err = jsondict['error']                                     
                errorobj = JsonRpcError(err['code'], err['message'], \
                    err['data']) 
                data = JsonRpcMessage.Error(jsondict['id'], errorobj)
                return JsonRpcParsed(JsonRpcParsedType.ERROR, data) 
            # no result, no error - id only             
            raise JsonRpcParseError(
                JsonRpcError.InvalidRequest('No reqired fields'))
        try:
            jsondict = json.loads(jsonstr)    
        except ValueError as e: 
            print '\r\n1--repr(e):' + repr(e)
            raise JsonRpcParseError(JsonRpcError.ParseError(jsonstr))
        try:
            parsedObjInfo = SubParseJsonRpcObject(jsondict)
        except JsonRpcParseError as e:
            raise                                         
        except Exception as e:                                         
            raise JsonRpcParseError(JsonRpcError.InternalError(str(e)))
        return parsedObjInfo

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
    def ParseError(cls, data = None):
        code = -32700
        message = 'Parse Error'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidRequest(cls, data = None):
        code = -32600
        message = 'Invalid Request'
        return JsonRpcError(code, message, data)

    @classmethod
    def MethodNotFound(cls, data = None):
        code = -32601
        message = 'Method Not Found'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidParams(cls, data = None):
        code = -32602
        message = 'Invalid Params'
        return JsonRpcError(code, message, data)

    @classmethod
    def InternalError(cls, data = None):   
        code = -32603
        message = 'Internal Error'
        return JsonRpcError(code, message, data)
        
#TODO: Batch request/response object ??