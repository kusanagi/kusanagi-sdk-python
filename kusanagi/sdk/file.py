# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import logging
import mimetypes
import os
import sys
import urllib.request
from typing import TYPE_CHECKING
from typing import List

from .lib.error import KusanagiError
from .lib.payload import ns

if TYPE_CHECKING:
    from .lib.payload.file import FileSchemaPayload
    from .lib.payload.file import HttpFileSchemaPayload

LOG = logging.getLogger(__name__)


class File(object):
    """
    File parameter.

    Actions receive files thought calls to a service component.

    Files can also be returned from the service actions.

    """

    def __init__(self, name: str, path: str = '', mime: str = '', filename: str = '', size: int = 0, token: str = ''):
        """
        Constructor.

        When the path is local it can start with "file://" or be a path to a local file,
        otherwise it means is a remote file and it must start with "http://".

        :param name: Name of the file parameter.
        :param path: Optional path to the file.
        :param mime: Optional MIME type of the file contents.
        :param filename: Optional file name and extension.
        :param size: Optional file size in bytes.
        :param token: Optional file server security token to access the file.

        :raises: ValueError, KusanagiError

        """

        if path and path.startswith('http://'):
            if not mime.strip():
                raise ValueError('File missing MIME type')
            elif not filename.strip():
                raise ValueError('File missing file name')
            elif size < 0:
                raise ValueError('Invalid file size')
            elif not token.strip():
                raise ValueError('File missing token')
        elif path:
            if token:
                raise ValueError('Unexpected file token')

            local_path = path[7:] if path.startswith('file://') else path
            if not os.path.isfile(local_path):
                raise KusanagiError(f'File doesn\'t exist: "{local_path}"')

            if not mime.strip():
                mime = mimetypes.guess_type(local_path)[0] or 'text/plain'

            if not filename.strip():
                filename = os.path.basename(local_path)

            if not size:
                try:
                    size = os.path.getsize(local_path)
                except OSError:  # pragma: no cover
                    size = 0

            if not path.startswith('file://'):
                path = f'file://{local_path}'

        self.__name = name
        self.__path = path
        self.__mime = mime
        self.__filename = filename
        self.__size = size
        self.__token = token

    def get_name(self) -> str:
        """Get the name of the file parameter."""

        return self.__name

    def get_path(self) -> str:
        """Get the file path."""

        return self.__path

    def get_mime(self) -> str:
        """Get the MIME type of the file contents."""

        return self.__mime

    def get_filename(self) -> str:
        """Get the file name."""

        return self.__filename

    def get_size(self) -> int:
        """Get the file size in bytes."""

        return self.__size

    def get_token(self) -> str:
        """Get the file server security token to access the file."""

        return self.__token

    def exists(self) -> bool:
        """Check if the file exists."""

        return self.__path != '' and not self.__path.startswith('file://')

    def is_local(self) -> bool:
        """Check if file is located in the local file system."""

        return self.__path.startswith('file://')

    def read(self) -> bytes:
        """
        Read the file contents.

        When the file is local it is read from the file system, otherwise
        an HTTP request is made to the remote file server to get its content.

        :raises: KusanagiError

        """

        # When the file is remote read it from the remote file server, otherwise
        # the file is a local file, so check if it exists and read its contents.
        if self.__path.startswith('http://'):
            # Prepare the headers for request
            headers = {}
            if self.__token:
                headers['X-Token'] = self.__token

            # Read file contents from remote file server
            request = urllib.request.Request(self.__path, headers=headers)
            try:
                with urllib.request.urlopen(request) as f:
                    return f.read()
            except Exception:
                raise KusanagiError(f'Failed to read file: "{self.__path}"')
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

    def copy_with_name(self, name: str) -> File:
        """
        Copy the file parameter with a new name.

        :param name: Name of the new file parameter.

        """

        return self.__class__(name, self.__path, self.__mime, self.__filename, self.__size, self.__token)

    def copy_with_mime(self, mime: str) -> File:
        """
        Copy the file parameter with a new MIME type.

        :param mime: MIME type of the new file parameter.

        """

        return self.__class__(self.__name, self.__path, mime, self.__filename, self.__size, self.__token)


class FileSchema(object):
    """File parameter schema in the framework."""

    def __init__(self, payload: FileSchemaPayload):
        self.__payload = payload

    def get_name(self) -> str:
        """Get file parameter name."""

        return self.__payload.get_name()

    def get_mime(self) -> str:
        """Get mime type."""

        return self.__payload.get([ns.MIME], 'text/plain')

    def is_required(self) -> bool:
        """Check if file parameter is required."""

        return self.__payload.get([ns.REQUIRED], False)

    def get_max(self) -> int:
        """
        Get maximum file size allowed for the parameter.

        Returns 0 if not defined.

        """

        return self.__payload.get([ns.MAX], sys.maxsize)

    def is_exclusive_max(self) -> bool:
        """
        Check if maximum size is inclusive.

        When max is not defined inclusive is False.

        """

        if not self.__payload.exists([ns.MAX]):
            return False

        return self.__payload.get([ns.EXCLUSIVE_MAX], False)

    def get_min(self) -> int:
        """
        Get minimum file size allowed for the parameter.

        Returns 0 if not defined.

        """

        return self.__payload.get([ns.MIN], 0)

    def is_exclusive_min(self) -> bool:
        """
        Check if minimum size is inclusive.

        When min is not defined inclusive is False.

        """

        if not self.__payload.exists([ns.MIN]):
            return False

        return self.__payload.get([ns.EXCLUSIVE_MIN], False)

    def get_http_schema(self) -> HttpFileSchema:
        """Get HTTP file param schema."""

        payload = self.__payload.get_http_file_schema_payload()
        return HttpFileSchema(payload)


class HttpFileSchema(object):
    """HTTP semantics of a file parameter schema in the framework."""

    def __init__(self, payload: HttpFileSchemaPayload):
        self.__payload = payload

    def is_accessible(self) -> bool:
        """Check if the Gateway has access to the parameter."""

        return self.__payload.get([ns.GATEWAY], True)

    def get_param(self) -> str:
        """Get name as specified via HTTP to be mapped to the name property."""

        return self.__payload.get([ns.PARAM], self.__payload.get_name())


def validate_file_list(files: List[File]):
    """
    Check that all the items in the list are File instances.

    :raises: ValueError

    """

    if not files:
        return

    for file in files:
        if not isinstance(file, File):
            raise ValueError(f'The file is not an instance of File: {file.__class__}')
