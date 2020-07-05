# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .lib.logging import INFO
from .lib.logging import value_to_log_string

if TYPE_CHECKING:
    from typing import Any
    from typing import List
    from typing import Union

    from .lib.payload.command import CommandPayload
    from .lib.payload.mapping import MappingPayload
    from .lib.payload.reply import ReplyPayload
    from .lib.state import State
    from .middleware import Middleware
    from .service import Service
    from .service import ServiceSchema


class Api(object):
    """API class for SDK components."""

    def __init__(self, component: Union[Middleware, Service], state: State):
        """
        Constructor.

        :param component: The framework component being run.
        :param state: The current state.

        """

        self._schemas: MappingPayload = state.context.get('schemas')
        self._component = component
        self._state = state
        self._logger = state.logger
        self._command: CommandPayload = state.context.get('command')
        self._reply: ReplyPayload = state.context.get('reply')

    def is_debug(self) -> bool:
        """Check if the component is running in debug mode."""

        return self._state.values.is_debug()

    def get_framework_version(self):
        """Get the KUSANAGI framework version."""

        return self._state.values.get_framework_version()

    def get_path(self) -> str:
        """Get source file path."""

        return os.path.dirname(self._state.values.get_path())

    def get_name(self) -> str:
        """Get component name."""

        return self._state.values.get_name()

    def get_version(self) -> str:
        """Get component version."""

        return self._state.values.get_version()

    def has_variable(self, name: str) -> bool:
        """
        Checks if a variable exists.

        :param name: Variable name.

        """

        return self._state.values.has_variable(name)

    def get_variables(self) -> dict:
        """Gets all component variables."""

        return self._state.values.get_variables()

    def get_variable(self, name: str) -> str:
        """
        Get a single component variable.

        :param name: Variable name.

        """

        return self._state.values.get_variable(name)

    def has_resource(self, name: str) -> bool:
        """
        Check if a resource name exist.

        :param name: Name of the resource.

        """

        return self._component.has_resource(name)

    def get_resource(self, name: str) -> Any:
        """
        Get a resource.

        :param name: Name of the resource.

        :raises: LookupError

        """

        return self._component.get_resource(name)

    def get_services(self) -> List[dict]:
        """Get service names and versions from the mapping schemas."""

        return list(self._schemas.get_services())

    def get_service_schema(self, name: str, version: str) -> ServiceSchema:
        """
        Get the schema for a service.

        The version can be either a fixed version or a pattern that uses "*"
        and resolves to the higher version available that matches.

        :param name: The name of the service.
        :para version: The version of the service.

        :raises: LookupError

        """

        from .service import ServiceSchema

        payload = self._schemas.get_service_schema_payload(name, version)
        return ServiceSchema(payload)

    def log(self, value: Any, level: int = INFO) -> Api:
        """
        Write a value to the KUSANAGI logs.

        Given value is converted to string before being logged.

        Output is truncated to have a maximum of 100000 characters.

        :param value: The value to log.
        :param level: An optional log level to use for the log message.

        """

        self._logger.log(level, value_to_log_string(value))
        return self

    def done(self) -> bool:
        """Dummy method to comply with KUSANAGI SDK specifications."""

        raise Exception('SDK does not support async call to end action: Api.done()')
