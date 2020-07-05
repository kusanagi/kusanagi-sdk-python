# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import Any
from typing import List

from .api import Api
from .lib.payload import ns
from .lib.payload.request import HttpRequestPayload
from .lib.payload.response import HttpResponsePayload
from .lib.payload.transport import TransportPayload
from .request import HttpRequest
from .transport import Transport


class Response(Api):
    """Response API class for the middleware component."""

    def get_gateway_protocol(self) -> str:
        """Get the protocol implemented by the gateway handling current request."""

        return self._command.get([ns.META, ns.PROTOCOL], '')

    def get_gateway_address(self) -> str:
        """Get public gateway address."""

        return self._command.get([ns.META, ns.GATEWAY], ['', ''])[1]

    def get_request_attribute(self, name: str, default: str = '') -> str:
        """
        Get a request attribute value.

        :param name: An attribute name.
        :param default: An optional default value to use when attribute is not defined.

        """

        return self._command.get([ns.META, ns.ATTRIBUTES, name], default)

    def get_request_attributes(self) -> dict:
        """Get all the request attributes."""

        return self._command.get([ns.META, ns.ATTRIBUTES], {})

    def get_http_request(self) -> HttpRequest:
        """Get HTTP request for current request."""

        payload = HttpRequestPayload(self._command.get([ns.REQUEST], {}))
        return HttpRequest(payload)

    def get_http_response(self) -> HttpResponse:
        """Get HTTP response for current request."""

        payload = HttpResponsePayload(self._reply.get([ns.RESPONSE], {}))
        payload.set_reply(self._reply)
        return HttpResponse(payload)

    def has_return(self) -> bool:
        """
        Check if there is a return value.

        Return value is available when the initial service that is called
        has a return value, and returned a value in its command reply.

        """

        return self._command.exists([ns.RETURN])

    def get_return(self) -> Any:
        """
        Get the return value returned by the called service.

        :raises: ValueError

        """

        if not self.has_return():
            service, version, action = self._command.get([ns.TRANSPORT, ns.META, ns.ORIGIN])
            raise ValueError(f'No return value defined on "{service}" ({version}) for action: "{action}"')

        return self._command.get([ns.RETURN])

    def get_transport(self) -> Transport:
        """Get the Transport object."""

        payload = TransportPayload(self._command.get_transport_data())
        return Transport(payload)


class HttpResponse(object):
    """HTTP response class."""

    def __init__(self, payload: HttpResponsePayload):
        """
        Constructor.

        :param payload: The payload with the HTTP response data.

        """

        self.__payload = payload
        self.__headers = {name.upper(): list(values) for name, values in payload.get([ns.HEADERS], {}).items()}

    def is_protocol_version(self, version: str) -> bool:
        """
        Check if the response uses the given HTTP version.

        :param version: The HTTP version.

        """

        return self.get_protocol_version() == version

    def get_protocol_version(self) -> str:
        """Get the HTTP version."""

        return self.__payload.get([ns.VERSION], '')

    def set_protocol_version(self, version: str) -> HttpResponse:
        """
        Set the HTTP version to the given protocol version.

        :param version: The HTTP version.

        """

        self.__payload.set([ns.VERSION], version)
        return self

    def is_status(self, status: str) -> bool:
        """
        Check if the response uses the given status.

        :param status: The HTTP status.

        """

        return self.get_status() == status

    def get_status(self) -> str:
        """Get the HTTP status."""

        return self.__payload.get([ns.STATUS], '')

    def get_status_code(self) -> int:
        """Get HTTP status code."""

        # Get the status code from the status message
        try:
            return int(self.get_status().split(' ', 1)[0])
        except (IndexError, ValueError):
            return 0

    def get_status_text(self) -> str:
        """Get HTTP status text."""

        try:
            return self.get_status().split(' ', 1)[1]
        except IndexError:
            return ''

    def set_status(self, code: int, text: str) -> HttpResponse:
        """
        Set the HTTP status to the given status.

        :param code: The HTTP status code.
        :param text: The HTTP status text.

        """

        self.__payload.set([ns.STATUS], f'{code} {text}')
        return self

    def has_header(self, name: str) -> bool:
        """
        Check if the HTTP header is defined.

        Header name is case insensitive.

        :param name: The HTTP header name.

        """

        return name.upper() in self.__headers

    def get_header(self, name: str, default: str = '') -> str:
        """
        Get an HTTP header value.

        Returns the HTTP header with the given name, or and empty string if not defined.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :param default: An optional default value.

        """

        name = name.upper()
        return self.__headers[name][0] if self.__headers.get(name) else default

    def get_header_array(self, name: str, default: List[str] = None) -> List[str]:
        """
        Gets an HTTP header value as an array.

        Header name is case insensitive.

        :param name: The HTTP header name.
        :param default: An optional default value.

        :raises: TypeError

        """

        if default is None:
            default = []
        elif not isinstance(default, list):
            raise TypeError('Default value is not a list')

        name = name.upper()
        return list(self.__headers[name]) if self.__headers.get(name) else default

    def get_headers(self) -> dict:
        """Get all HTTP headers."""

        return {key: values[0] for key, values in self.__payload.get([ns.HEADERS], {}).items()}

    def get_headers_array(self) -> dict:
        """Get all HTTP headers."""

        return {key: list(values) for key, values in self.__payload.get([ns.HEADERS], {}).items()}

    def set_header(self, name: str, value: str, overwrite: bool = False) -> HttpResponse:
        """
        Set an HTTP header with the given name and value.

        :param name: The HTTP header.
        :param value: The header value.
        :param overwrite: Optional value to allow existing headers to be overwritten.

        """

        # Make sure the value is a string
        if not isinstance(value, str):
            value = str(value)

        # If it exists get the original header name from the payload headers
        uppercase_name = name.upper()
        original_name = None
        for header_name in self.__payload.get([ns.HEADERS]).keys():
            if header_name.upper() == uppercase_name:
                original_name = header_name
                break

        # When a similar header exists replace the old header name with the new name
        # and add the new value. This can happen when the header name casing is different.
        if original_name and original_name != name:
            values = [] if overwrite else list(self.__headers[uppercase_name])
            values.append(value)
            # Remove the header with the previous name
            self.__payload.delete([ns.HEADERS, original_name])
            # Add the header with the new name
            self.__payload.set([ns.HEADERS, name], values)
        elif overwrite:
            self.__payload.set([ns.HEADERS, name], [value])
        else:
            self.__payload.append([ns.HEADERS, name], value)

        # Update the list of cached headers
        if uppercase_name in self.__headers and not overwrite:
            self.__headers[uppercase_name].append(value)
        else:
            self.__headers[uppercase_name] = [value]

        return self

    def has_body(self) -> bool:
        """Check if the response has content."""

        return self.get_body() != b''

    def get_body(self) -> bytes:
        """Get the response body content."""

        return self.__payload.get([ns.BODY], b'')

    def set_body(self, content: bytes = b'') -> HttpResponse:
        """
        Set the content of the HTTP response body.

        :param content: The content for the HTTP response body.

        """

        self.__payload.set([ns.BODY], content)
        return self
