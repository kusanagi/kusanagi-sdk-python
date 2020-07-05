# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from .api import Api
from .file import File
from .lib.payload import ns
from .lib.payload.request import HttpRequestPayload
from .lib.payload.utils import param_to_payload
from .lib.payload.utils import payload_to_file
from .lib.payload.utils import payload_to_param
from .param import Param

if TYPE_CHECKING:
    from typing import Any
    from typing import List
    from urllib.parse import ParseResult

    from .response import Response


class Request(Api):
    """Request API class for the middleware component."""

    DEFAULT_RESPONSE_STATUS_CODE = 200
    DEFAULT_RESPONSE_STATUS_TEXT = 'OK'

    def __init__(self, *args, **kwargs):
        """Constructor."""

        super().__init__(*args, **kwargs)
        # Index parameters by name
        self.__params = {param[ns.NAME]: param for param in self._reply.get([ns.CALL, ns.PARAMS], [])}

    def get_id(self) -> str:
        """Get the request UUID."""

        return self._command.get([ns.META, ns.ID], '')

    def get_timestamp(self) -> str:
        """Get the request timestamp."""

        return self._command.get([ns.META, ns.DATETIME], '')

    def get_gateway_protocol(self) -> str:
        """Get the protocol implemented by the gateway handling current request."""

        return self._command.get([ns.META, ns.PROTOCOL], '')

    def get_gateway_address(self) -> str:
        """Get public gateway address."""

        return self._command.get([ns.META, ns.GATEWAY], ['', ''])[1]

    def get_client_address(self) -> str:
        """Get IP address and port of the client which sent the request."""

        return self._command.get([ns.META, ns.CLIENT], '')

    def set_attribute(self, name: str, value: str) -> Request:
        """
        Register a request attribute.

        :raises: TypeError

        """

        if not isinstance(value, str):
            raise TypeError('Attribute value must be a string')

        self._reply.set([ns.ATTRIBUTES, name], value)
        return self

    def get_service_name(self) -> str:
        """Get the name of the service."""

        return self._reply.get([ns.CALL, ns.SERVICE], '')

    def set_service_name(self, service: str) -> Request:
        """
        Set the name of the service.

        :param service: The service name.

        """

        self._reply.set([ns.CALL, ns.SERVICE], service)
        return self

    def get_service_version(self) -> str:
        """Get the version of the service."""

        return self._reply.get([ns.CALL, ns.VERSION], '')

    def set_service_version(self, version: str) -> Request:
        """
        Set the version of the service.

        :param version: The service version.

        """

        self._reply.set([ns.CALL, ns.VERSION], version)
        return self

    def get_action_name(self) -> str:
        """Get the name of the action."""

        return self._reply.get([ns.CALL, ns.ACTION], '')

    def set_action_name(self, action: str) -> Request:
        """
        Set the name of the action.

        :param action: The action name.

        """

        self._reply.set([ns.CALL, ns.ACTION], action)
        return self

    def has_param(self, name: str) -> bool:
        """
        Check if a parameter exists.

        :param name: The parameter name.

        """

        return name in self.__params

    def get_param(self, name: str) -> Param:
        """
        Get a request parameter.

        :param name: The parameter name.

        """

        if not self.has_param(name):
            return Param(name)

        return payload_to_param(self.__params[name])

    def get_params(self) -> List[Param]:
        """Get all request parameters."""

        return [payload_to_param(payload) for payload in self.__params.values()]

    def set_param(self, param: Param) -> Request:
        """
        Add a new param for current request.

        :param param: The parameter.

        """

        payload = param_to_payload(param)
        self.__params[param.get_name()] = payload
        self._reply.append([ns.CALL, ns.PARAMS], payload)
        return self

    def new_param(self, name: str, value: Any = '', type: str = '') -> Param:
        """
        Creates a new parameter object.

        Creates an instance of Param with the given name, and optionally the value and data type.
        When the value is not provided then an empty string is assumed.
        If the data type is not defined then "string" is assumed.

        :param name: The parameter name.
        :param value: The parameter value.
        :param type: The data type of the value.

        :raises: TypeError

        """

        return Param(name, value=value, type=type, exists=True)

    def new_response(
        self,
        code: int = DEFAULT_RESPONSE_STATUS_CODE,
        text: str = DEFAULT_RESPONSE_STATUS_TEXT,
    ) -> Response:
        """
        Create a new Response object.

        :param code: Optional status code.
        :param text: Optional status text.

        """

        from .response import Response

        response = Response(self._component, self._state)
        response.get_http_response().set_status(code, text)
        # Change the reply payload from a request payload to a response payload.
        # Initially the reply for the Request component is a RequestPayload.
        self._reply.set_response(code, text)
        return response

    def get_http_request(self) -> HttpRequest:
        """Get HTTP request for current request."""

        payload = HttpRequestPayload(self._command.get([ns.REQUEST], {}))
        return HttpRequest(payload)


class HttpRequest(object):
    """HTTP request class."""

    METHOD_CONNECT = 'CONNECT'
    METHOD_TRACE = 'TRACE'
    METHOD_HEAD = 'HEAD'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_PATCH = 'PATCH'
    METHOD_DELETE = 'DELETE'

    def __init__(self, payload: HttpRequestPayload):
        """
        Constructor.

        :param payload: The payload with the HTTP request data.

        """

        self.__payload = payload
        self.__headers = {name.upper(): values for name, values in payload.get([ns.HEADERS], {}).items()}
        self.__url: ParseResult = urlparse(self.__payload.get([ns.URL], ''))
        # TODO: Change this to make each file a list to support multiple files with same name
        self.__files = {p[ns.NAME]: payload_to_file(p) for p in self.__payload.get([ns.FILES], [])}

    def is_method(self, method: str) -> bool:
        """
        Determine if the request used the given HTTP method.

        :param method: The HTTP method.

        """

        return self.__payload.get([ns.METHOD]) == method.upper()

    def get_method(self) -> str:
        """Get the HTTP method."""

        return self.__payload.get([ns.METHOD], '').upper()

    def get_url(self) -> str:
        """Get request URL."""

        return self.__url.geturl()

    def get_url_scheme(self) -> str:
        """Get request URL scheme."""

        return self.__url.scheme

    def get_url_host(self) -> str:
        """Get request URL host."""

        # The port number is ignored when present
        return self.__url.netloc.split(':')[0]

    def get_url_port(self) -> int:
        """Get request URL port."""

        return self.__url.port or 0

    def get_url_path(self) -> str:
        """Get request URL path."""

        return self.__url.path.rstrip('/')

    def has_query_param(self, name: str) -> bool:
        """
        Check if a param is defined in the HTTP query string.

        :param name: The HTTP param name.

        """

        return name in self.__payload.get([ns.QUERY], {})

    def get_query_param(self, name: str, default: str = '') -> str:
        """
        Get the param value from the HTTP query string.

        The first value is returned when the parameter is present more
        than once in the HTTP query string.

        :param name: The HTTP param name.
        :param default: An optional default value.

        """

        if not self.has_query_param(name):
            return default

        # The query param value is always an array that contains the
        # actual parameter values. A param can have many values when
        # the HTTP string contains the parameter more than once.
        value = self.__payload.get([ns.QUERY, name], [])
        return value[0] if value else default

    def get_query_param_array(self, name: str, default: List[str] = None) -> List[str]:
        """
        Get the param value from the HTTP query string.

        The result is a list with all the values for the parameter.
        A parameter can be present more than once in an HTTP query string.

        :param name: The HTTP param name.
        :param default: An optional default value.

        :raises: TypeError

        """

        if default is None:
            default = []
        elif not isinstance(default, list):
            raise TypeError('Default value is not a list')

        values = self.__payload.get([ns.QUERY, name])
        return list(values) if values else default

    def get_query_params(self) -> dict:
        """
        Get all HTTP query params.

        The first value of each parameter is returned when the parameter
        is present more than once in the HTTP query string.

        """

        return {key: values[0] for key, values in self.__payload.get([ns.QUERY], {}).items()}

    def get_query_params_array(self) -> dict:
        """
        Get all HTTP query params.

        Each parameter value is returned as a list.

        """

        return {key: list(values) for key, values in self.__payload.get([ns.QUERY], {}).items()}

    def has_post_param(self, name: str) -> bool:
        """
        Check if a param is defined in the HTTP POST contents.

        :param name: The HTTP param name.

        """

        return name in self.__payload.get([ns.POST_DATA], {})

    def get_post_param(self, name: str, default: str = '') -> str:
        """
        Get the param value from the HTTP POST contents.

        The first value is returned when the parameter is present more
        than once in the HTTP request.

        :param name: The HTTP param name.
        :param default: An optional default value.

        """

        if not self.has_post_param(name):
            return default

        # The query param value is always an array that contains the
        # actual parameter values. A param can have many values when
        # the HTTP request contains the parameter more than once.
        value = self.__payload.get([ns.POST_DATA, name], [])
        return value[0] if value else default

    def get_post_param_array(self, name: str, default: List[str] = None) -> List[str]:
        """
        Get the param value from the HTTP POST contents.

        The result is a list with all the values for the parameter.
        A parameter can be present more than once in an HTTP request.

        :param name: The HTTP param name.
        :param default: An optional default value.

        :raises: TypeError

        """

        if default is None:
            default = []
        elif not isinstance(default, list):
            raise TypeError('Default value is not a list')

        values = self.__payload.get([ns.POST_DATA, name])
        return list(values) if values else default

    def get_post_params(self) -> dict:
        """
        Get all HTTP POST params

        The first value of each parameter is returned when the parameter
        is present more than once in the HTTP request.

        """

        return {key: values[0] for key, values in self.__payload.get([ns.POST_DATA], {}).items()}

    def get_post_params_array(self) -> dict:
        """
        Get all HTTP POST params.

        Each parameter value is returned as a list.

        """

        return {key: list(values) for key, values in self.__payload.get([ns.POST_DATA], {}).items()}

    def is_protocol_version(self, version: str) -> bool:
        """
        Check if the request used the given HTTP version.

        :param version: The HTTP version.

        """

        return self.__payload.get([ns.VERSION]) == version

    def get_protocol_version(self) -> str:
        """Get the HTTP version."""

        return self.__payload.get([ns.VERSION], '')

    def has_header(self, name: str) -> bool:
        """
        Check if the HTTP header is defined.

        Header name is case insensitive.

        :param name: The HTTP header name.

        """

        return name.upper() in self.__headers

    def get_header(self, name: str, default: str = '') -> str:
        """
        Get an HTTP header.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :param default: An optional default value.

        """

        # The header value is always an array that contains the actual header values.
        # A header can have many values when the HTTP request contains the header more than once.
        value = self.__headers.get(name.upper())
        return value[0] if value else default

    def get_header_array(self, name: str, default: List[str] = None) -> List[str]:
        """
        Get an HTTP header.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :param default: An optional default value.

        :raises: TypeError

        """

        if default is None:
            default = []
        elif not isinstance(default, list):
            raise TypeError('Default value is not a list')

        values = self.__headers.get(name.upper())
        return list(values) if values else default

    def get_headers(self) -> dict:
        """
        Get all HTTP headers.

        The first value of each header is returned when the header
        is present more than once in the HTTP request.

        """

        return {key: value[0] for key, value in self.__payload.get([ns.HEADERS], {}).items()}

    def get_headers_array(self) -> dict:
        """
        Get all HTTP headers.

        Each parameter value is returned as a list.

        """

        return {key: list(values) for key, values in self.__payload.get([ns.HEADERS], {}).items()}

    def has_body(self) -> bool:
        """Check if the HTTP request body has content."""

        return self.__payload.get([ns.BODY], b'') != b''

    def get_body(self) -> bytes:
        """Get the HTTP request body."""

        return self.__payload.get([ns.BODY], b'')

    def has_file(self, name: str) -> bool:
        """
        Check if a file was uploaded in current request.

        :param name: A file name.

        """

        return name in self.__files

    def get_file(self, name: str) -> File:
        """
        Get an uploaded file.

        :param name: The name of the file.

        """

        # When the file doesnt exist return an empty file
        if not self.has_file(name):
            return File(name)

        return self.__files[name]

    def get_files(self) -> List[File]:
        """Get uploaded files."""

        return list(self.__files.values())
