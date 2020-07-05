# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from . import Payload
from . import ns


class ParamSchemaPayload(Payload):
    """Handle operations on a parameter schema payload."""

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name = name

    def get_name(self) -> str:
        return self.__name

    def get_http_param_schema_payload(self) -> 'HttpParamSchemaPayload':
        name = self.get_name()
        return HttpParamSchemaPayload(name, self.get([ns.HTTP], {}))


class HttpParamSchemaPayload(Payload):
    """Handle operations on an HTTP parameter schema payload."""

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name = name

    def get_name(self) -> str:
        return self.__name
