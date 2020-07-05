# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING

from .action import ActionSchema
from .component import Component
from .lib.payload import ns

if TYPE_CHECKING:
    from typing import Awaitable
    from typing import Callable
    from typing import List
    from typing import Union

    from .action import Action
    from .lib.asynchronous import AsyncAction
    from .lib.payload.service import HttpServiceSchemaPayload
    from .lib.payload.service import ServiceSchemaPayload

    AsyncCallback = Callable[[AsyncAction], Awaitable[AsyncAction]]
    Callback = Callable[[Action], Action]


class Service(Component):
    """KUSANAGI service component."""

    def action(self, name: str, callback: Union[Callback, AsyncCallback]) -> Service:
        """
        Set a callback for an action.

        :param name: The name of the service action.
        :param callback: Callback to handle action calls.

        """

        self._callbacks[name] = callback
        return self


class ServiceSchema(object):
    """Service schema in the framework."""

    def __init__(self, payload: ServiceSchemaPayload):
        """
        Constructor.

        :param payload: The payload for the service schema.

        """

        self.__payload = payload

    def get_name(self) -> str:
        """Get service name."""

        return self.__payload.get_name()

    def get_version(self) -> str:
        """Get service version."""

        return self.__payload.get_version()

    def get_address(self) -> str:
        """Get the network address of the service."""

        return self.__payload.get([ns.ADDRESS], '')

    def has_file_server(self) -> bool:
        """Check if service has a file server."""

        return self.__payload.get([ns.FILES], False)

    def get_actions(self) -> List[str]:
        """Get the names of the service actions."""

        return self.__payload.get_action_names()

    def has_action(self, name: str) -> bool:
        """
        Check if an action exists for current service schema.

        :param name: The action name.

        """

        return name in self.get_actions()

    def get_action_schema(self, name: str) -> ActionSchema:
        """
        Get schema for an action.

        :param name: The action name.

        :raises: LookupError

        """

        payload = self.__payload.get_action_schema_payload(name)
        return ActionSchema(name, payload)

    def get_http_schema(self) -> HttpServiceSchema:
        """Get HTTP service schema."""

        payload = self.__payload.get_http_service_schema_payload()
        return HttpServiceSchema(payload)


class HttpServiceSchema(object):
    """HTTP semantics of a service schema in the framework."""

    def __init__(self, payload: HttpServiceSchemaPayload):
        """
        Constructor.

        :param payload: The payload for the HTTP service schema.

        """

        self.__payload = payload

    def is_accessible(self) -> bool:
        """Check if the gateway has access to the service."""

        return self.__payload.get([ns.GATEWAY], True)

    def get_base_path(self) -> str:
        """Get base HTTP path for the service."""

        return self.__payload.get([ns.BASE_PATH], '')
