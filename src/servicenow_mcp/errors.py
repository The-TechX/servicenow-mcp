class ServiceNowError(RuntimeError): pass
class AuthenticationError(ServiceNowError): pass
class ResponseError(ServiceNowError): pass
class RecordNotFoundError(ServiceNowError): pass
class ParseError(ServiceNowError): pass
