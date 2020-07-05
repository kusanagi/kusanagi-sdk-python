# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import asyncio
import io
import os
import urllib
from http.client import parse_headers
from typing import TYPE_CHECKING

from ..action import EXECUTION_TIMEOUT
from ..action import Action
from ..file import File
from ..file import validate_file_list
from ..param import validate_parameter_list
from ..request import HttpRequest
from ..request import Request
from ..response import Response
from ..transport import Transport
from .call import AsyncClient
from .error import KusanagiError
from .payload import ns
from .payload.request import HttpRequestPayload
from .payload.transport import TransportPayload

if TYPE_CHECKING:
    from typing import Any
    from typing import List

    from ..param import Param


def file_to_async(f: File) -> AsyncFile:
    """
    Convert file to an async file

    :param f: The file to convert.

    """

    return AsyncFile(
        f.get_name(),
        f.get_path(),
        mime=f.get_mime(),
        filename=f.get_filename(),
        size=f.get_size(),
        token=f.get_token(),
    )


class AsyncRequest(Request):
    """Request API class for the middleware component."""

    def get_http_request(self) -> AsyncHttpRequest:
        """Get HTTP request for current request."""

        payload = HttpRequestPayload(self._command.get([ns.REQUEST], {}))
        return AsyncHttpRequest(payload)


class AsyncHttpRequest(HttpRequest):
    """HTTP request class."""

    def __init__(self, payload: HttpRequestPayload):
        """
        Constructor.

        :param payload: The payload with the HTTP request data.

        """

        super().__init__(payload)
        # Convert the files to async files
        self.__files = {name: file_to_async(file) for name, file in self.__files}

    def get_file(self, name: str) -> AsyncFile:
        """
        Get an uploaded file.

        :param name: The name of the file.

        """

        return super().get_file(name)

    def get_files(self) -> List[AsyncFile]:
        """Get uploaded files."""

        return super().get_files()


class AsyncResponse(Response):
    """Response API class for the middleware component."""

    def get_transport(self) -> AsyncTransport:
        """Get the Transport object."""

        payload = TransportPayload(self._command.get_transport_data())
        return AsyncTransport(payload)


class AsyncTransport(Transport):
    """Transport class encapsulates the transport object."""

    def get_download(self) -> AsyncFile:
        """Get the file download defined for the response."""

        return file_to_async(super().get_download())


class AsyncAction(Action):
    """Action API class for service component."""

    def get_file(self, name: str) -> AsyncFile:
        """
        Get a file with a given name.

        :param name: File name.

        """

        # TODO: Create the file from the service schema (see PHP SDK)
        if not self.has_file(name):
            return AsyncFile(name)

        return file_to_async(super().get_file(name))

    def new_file(self, name: str, path: str, mime: str = '') -> AsyncFile:
        """
        Create a new file.

        :param name: File name.
        :param path: File path.
        :param mime: Optional file mime type.

        """

        return AsyncFile(name, path, mime=mime)

    async def call(
        self,
        service: str,
        version: str,
        action: str,
        params: List[Param] = None,
        files: List[File] = None,
        timeout: int = EXECUTION_TIMEOUT,
    ) -> Any:
        """
        Perform a run-time call to a service.

        The result of this call is the return value from the remote action.

        :param service: The service name.
        :param version: The service version.
        :param action: The action name.
        :param params: Optional list of Param objects.
        :param files: Optional list of File objects.
        :param timeout: Optional timeout in milliseconds.

        :raises: ValueError, KusanagiError

        """

        # Check that the call exists in the config
        service_title = f'"{service}" ({version})'
        try:
            schema = self.get_service_schema(self.get_name(), self.get_version())
            action_schema = schema.get_action_schema(self.get_action_name())
            if not action_schema.has_call(service, version, action):
                msg = f'Call not configured, connection to action on {service_title} aborted: "{action}"'
                raise KusanagiError(msg)
        except LookupError as err:
            raise KusanagiError(err)

        # Check that the remote action exists and can return a value, and if it doesn't issue a warning
        try:
            remote_action_schema = self.get_service_schema(service, version).get_action_schema(action)
        except LookupError as err:  # pragma: no cover
            self._logger.warning(err)
        else:
            if not remote_action_schema.has_return():
                raise KusanagiError(f'Cannot return value from {service_title} for action: "{action}"')

        validate_parameter_list(params)
        validate_file_list(files)

        # Check that the file server is enabled when one of the files is local
        if files:
            for file in files:
                if file.is_local():
                    # Stop checking when one local file is found and the file server is enables
                    if schema.has_file_server():
                        break

                    raise KusanagiError(f'File server not configured: {service_title}')

        return_value = None
        transport = None
        client = AsyncClient(self._logger, tcp=self._state.values.is_tcp_enabled())
        try:
            # NOTE: The transport set to the call won't have any data added by the action component
            return_value, transport = await client.call(
                schema.get_address(),
                self.get_action_name(),
                [service, version, action],
                timeout,
                transport=TransportPayload(self._command.get_transport_data()),  # Use a clean transport for the call
                params=params,
                files=files,
            )
        finally:
            # Always add the call info to the transport, even after an exception is raised during the call
            self._transport.add_call(
                self.get_name(),
                self.get_version(),
                self.get_action_name(),
                service,
                version,
                action,
                client.get_duration(),
                params=params,
                files=files,
                timeout=timeout,
                transport=transport,
            )

        return return_value


def AsyncFile(File):
    """
    File parameter.

    Actions receive files thought calls to a service component.

    Files can also be returned from the service actions.

    """

    async def read(self) -> bytes:
        """
        Read the file contents.

        When the file is local it is read from the file system, otherwise
        an HTTP request is made to the remote file server to get its content.

        :raises: KusanagiError

        """

        # When the file is remote read it from the remote file server, otherwise
        # the file is a local file, so check if it exists and read its contents.
        if self.__path.startswith('http://'):
            # Parse the remote file URL and open a connection to the file server
            url = urllib.parse.urlsplit(self.__path)
            reader, writer = await asyncio.open_connection(url.hostname, 80)
            # Prepare the HTTP request
            request = [
                f'GET {url.path} HTTP/1.0',
                f'Host: {url.hostname}',
                f'X-Token: {self.__token}',
                '\r\n'
            ]
            writer.write('\r\n'.join(request).encode('utf8'))
            try:
                # Make the request
                response = io.BytesIO(await reader.read())
                # Remove the HTTP response start line to allow header parsing
                response.readline()
                # Parse the headers to be able to read only the response body from the response
                parse_headers(response)
                # read the file contents from the response body
                return response.read()
            except asyncio.CancelledError:
                raise
            except Exception:
                raise KusanagiError(f'Failed to read file: "{self.__path}"')
            finally:
                writer.close()
        elif os.path.isfile(self.__path[7:]):
            try:
                # Read the local file contents
                with open(self.__path[7:], 'rb') as f:
                    return f.read()
            except Exception:
                raise KusanagiError(f'Failed to read file: "{self.__path}"')
        else:
            # The file is local and can't be read
            raise KusanagiError(f'File does not exist in path: "{self.__path}"')
