# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from . import Payload
from . import ns


class FileSchemaPayload(Payload):
    """Handle operations on a file parameter schema payload."""

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name = name

    def get_name(self) -> str:
        return self.__name or ''

    def get_http_file_schema_payload(self) -> 'HttpFileSchemaPayload':
        name = self.get_name()
        return HttpFileSchemaPayload(name, self.get([ns.HTTP], {}))


class HttpFileSchemaPayload(Payload):
    """Handle operations on an HTTP file parameter schema payload."""

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name = name

    def get_name(self) -> str:
        return self.__name
