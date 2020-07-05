# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import List

from . import Payload
from . import ns
from .action import ActionSchemaPayload


class ServiceSchemaPayload(Payload):
    """Handles operations on a Service schema payload."""

    def __init__(self, *args, name: str = None, version: str = None, **kwargs):
        """
        Constructor.

        :param name: Optional service name.
        :param version: Optional service version.

        """

        super().__init__(*args, **kwargs)
        self.__name = name
        self.__version = version

    def get_name(self) -> str:
        """Get the service name."""

        return self.__name or ''

    def get_version(self) -> str:
        """Get the service version."""

        return self.__version or ''

    def get_action_names(self) -> List[str]:
        """Get the names of the service actions."""

        return list(self.get([ns.ACTIONS], {}).keys())

    def get_action_schema_payload(self, name: str) -> ActionSchemaPayload:
        """
        Get an action schema payload.

        :param name: The name of the action to get.

        :raises: LookupError

        """

        actions = self.get([ns.ACTIONS], {})
        if name not in actions:
            raise LookupError(f'Cannot resolve schema for action: {name}')

        return ActionSchemaPayload(actions[name])

    def get_http_service_schema_payload(self) -> 'HttpServiceSchemaPayload':
        """Get the HTTP service schema payload."""

        return HttpServiceSchemaPayload(self.get([ns.HTTP], {}))


class HttpServiceSchemaPayload(Payload):
    """Handles operations on a HTTP service schema payload."""
