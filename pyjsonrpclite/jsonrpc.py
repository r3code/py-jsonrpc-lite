#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

class JsonRpcException(Exception):
    """Base class for exceptions in this module."""
    pass


class JsonRpcParseError(Exception):
    """Raised if Parse JSON-RPC 2.0 string failed.
    Params:
        rpcError - `JsonRpcError` """  
    def __init__(self, rpcError):
        Exception.__init__(self, rpcError)         
        self.rpcError = rpcError         


def defaultJsonEncode(o):
    return o.__dict__ 


class JsonRpcMessage(object):

    @classmethod
    def Request(cls, id, method, params = None):
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
        if not params is None:
            self.params = params


class JsonRpcNotification(JsonRpcRequest):
    '''JSON-RPC 2.0 Notification object'''
    def __init__(self, method, params = None):
        JsonRpcRequest.__init__(self, None, method, params)
        del self.id
        

class JsonRpcSuccessResponse(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request success'''
    def __init__(self, id, result):
        self.id = id
        self.result = result


class JsonRpcErrorResponse(JsonRpcMessage):
    '''JSON-RPC 2.0 Response Object reporting request error.
    Params:
        id -- errornous request id or None,
        err - `JsonRpcError` object with an error data 
    '''
    def __init__(self, id, err):
        self.id = id
        self.error = err


class JsonRpcParsedType(object):
    '''Types used by parser to identify parsedType result in `JsonRpcParsed`'''
    INVALID = 'INVALID'
    REQUEST = 'REQUEST'
    NOTIFICATION = 'NOTIFICATION'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'    
    

class JsonRpcParsed(object):
    '''Presents a json string parse result: parsedType and payload.
    Params:
        parsedType  -- <Enum|`JsonRpcParsedType`>,
        payload     -- `JsonRpcMessage`'''
    def __init__(self, parsedType, payload):
        self.parsedType = parsedType
        self.payload = payload 

    @classmethod
    def Parse(cls, jsonstr):
        '''Parses json formatted string. 
        Raises `JsonRpcParseError` if Parse fails. 
        Return a `JsonRpcParsed`.'''
        
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
            Raises `JsonRpcException` in case of error'''
            if not 'jsonrpc' in jsondict:
                raise JsonRpcException('Message have no "jsonrpc" field')
            if jsondict['jsonrpc'] <> '2.0':                                    
                raise JsonRpcException('"jsonrpc" field value should be 2.0') 

        def SubValidateMethod(jsondict): 
            '''Checks if method field exists and has correct value'''
            if not SubHasMethod(jsondict):
                raise JsonRpcException('No "method" field')
            if not SubIsMethodCorrect(jsondict):
                raise JsonRpcException('Invalid "method" field value')                         

        def SubValidateErrorObj(errdict):
            '''Checks if Error object has JSON-RPC 2.0 required fields. '''
            hasCode = 'code' in errdict
            hasMessage = 'message' in errdict
            if not (hasCode and hasMessage):
                raise JsonRpcException('Invalid JSON-RPC 2.0 Error object structure')
            allowedCodes = [-32700]
            allowedCodes = allowedCodes + [x for x in range(-32603, -32599)]
            allowedCodes = allowedCodes + [x for x in range(-32099,-31999)]    
            if not errdict['code'] in allowedCodes:
                raise JsonRpcException('Invalid JSON-RPC 2.0 Error code')    

        def SubParseNotification(jsondict): 
            '''Parses jsondict, validates JSON-RPC 2.0 Notification structure and values.
            Doesn't check JSON-RPC 2.0 "jsonrpc" and "id".
            Raises `JsonRpcParseError` if parse failed, or params invalid.'''   
            try: 
                SubValidateMethod(jsondict)       
            except JsonRpcException as e:                    
                raise JsonRpcParseError(JsonRpcError.InvalidRequest(str(e)))
            params = jsondict.get('params', None)
            payload = JsonRpcMessage.Notification(jsondict['method'], params)
            return JsonRpcParsed(JsonRpcParsedType.NOTIFICATION, payload)                   

        def SubParseRequest(jsondict):
            '''Parses jsondict, validates JSON-RPC 2.0 Request structure and values.
            Doesn't check JSON-RPC 2.0 "jsonrpc","id", "method".
            Raises `JsonRpcParseError` if parse failed, or params invalid.''' 
            id = jsondict['id'] 
            method = jsondict['method']            
            params = jsondict.get('params', None)             
            payload = JsonRpcMessage.Request(id, method, params)
            return JsonRpcParsed(JsonRpcParsedType.REQUEST, payload)

        def SubParseSuccessResponse(jsondict):
            '''Parses jsondict, validates JSON-RPC 2.0 Response Success structure and values.
            Doesn't check JSON-RPC 2.0 "jsonrpc","id".
            Raises `JsonRpcParseError` if parse failed, or result invalid.
            Params:
                jsondict - object, json parsed object
            '''
            payload = JsonRpcMessage.Success(jsondict['id'], jsondict['result'])
            return JsonRpcParsed(JsonRpcParsedType.SUCCESS, payload)  

        def SubParseErrorResponse(jsondict):
            '''Parses jsondict, validates JSON-RPC 2.0 Response Error structure and values.
            Doesn't check JSON-RPC 2.0 "jsonrpc","id".
            Raises `JsonRpcParseError` if parse failed, or error object invalid.
            Params:
                jsondict - object, json parsed object
            '''
            err = jsondict.get('error', None)   
            try:
                SubValidateErrorObj(err)
                errorobj = JsonRpcError(err['code'], err['message'], \
                    err.get('data', None)) 
                payload = JsonRpcMessage.Error(jsondict['id'], errorobj)
                return JsonRpcParsed(JsonRpcParsedType.ERROR, payload) 
            except JsonRpcException as e:
                raise JsonRpcParseError(JsonRpcError.InvalidParams(str(e)))

        def SubParseJsonRpcObject(jsondict):
            '''Check if jsondict is valid JSON-RPC 2.0 object.
            Raises `JsonRpcParseError` if parse/validation failed.
            Returns `JsonRpcParsed` object containing Parse results.'''
            try:
                SubValidateHeader(jsondict)
            except JsonRpcException as e:
                raise JsonRpcParseError(JsonRpcError.InvalidRequest(str(e)))

            isNotification = not SubHasValidId(jsondict)
            if isNotification:  
                return SubParseNotification(jsondict)

            #else it has Id so it may be: request, success, error message
            isRequest = SubIsMethodCorrect(jsondict)
            if isRequest: 
                return SubParseRequest(jsondict)

            # no METHOD field so it may be: success, error message
            isSuccessMsg = 'result' in jsondict
            if isSuccessMsg:
                return SubParseSuccessResponse(jsondict)

            isErrorMsg = 'error' in jsondict
            if isErrorMsg:
                return SubParseErrorResponse(jsondict)
            # no result, no error, no method - id only
            raise JsonRpcParseError(
                JsonRpcError.InvalidRequest('No reqired fields'))
        try:
            jsondict = json.loads(jsonstr)    
        except ValueError as e: 
            raise JsonRpcParseError(JsonRpcError.ParseError(jsonstr))
        try:
            parsedObjInfo = SubParseJsonRpcObject(jsondict)
        except JsonRpcParseError as e:
            raise
        except Exception as e:
            raise JsonRpcParseError(JsonRpcError.InternalError(str(e)))
        return parsedObjInfo

class JsonRpcError(object):
    '''Class implements JSON-RPC 2.0 Error Object.
    Params:
        code -- negative int number JSON-RPC 2.0 error code,
        message -- string, error message,
        data -- any type, extra info (may be ommited)
    '''

    def __init__(self, code, message, data = None):
        self.code = code
        self.message = message 
        if not data is None:
            self.data = data

    @classmethod
    def Error(cls, code, message, data = None): 
        '''Creates common Error object.'''
        return JsonRpcError(code, message, data)

    @classmethod
    def ParseError(cls, data = None):
        '''Creates `JsonRpcError` instance for prdefined JSON-RPC 2.0 error. 
        Code -32700. Invalid JSON was received by the server.
        An error occurred on the server while parsing the JSON text.
        '''
        code = -32700
        message = 'Parse Error'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidRequest(cls, data = None):
        '''Creates `JsonRpcError` instance for prdefined JSON-RPC 2.0 error. 
        Code -32600. The JSON sent is not a valid Request object.'''
        code = -32600
        message = 'Invalid Request'
        return JsonRpcError(code, message, data)

    @classmethod
    def MethodNotFound(cls, data = None):
        '''Creates `JsonRpcError` instance for prdefined JSON-RPC 2.0 error. 
        Code -32601. The method does not exist / is not available.'''
        code = -32601
        message = 'Method Not Found'
        return JsonRpcError(code, message, data)

    @classmethod
    def InvalidParams(cls, data = None): 
        '''Creates `JsonRpcError` instance for prdefined JSON-RPC 2.0 error. 
        Code -32602. Invalid method parameter(s).'''
        code = -32602
        message = 'Invalid Params'
        return JsonRpcError(code, message, data)

    @classmethod
    def InternalError(cls, data = None):  
        '''Creates `JsonRpcError` instance for prdefined JSON-RPC 2.0 error. 
        Code -32603. Internal JSON-RPC error.''' 
        code = -32603
        message = 'Internal Error'
        return JsonRpcError(code, message, data)
