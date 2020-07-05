# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING

from .lib.events import Events
from .lib.logging import INFO
from .lib.logging import Logger
from .lib.logging import value_to_log_string
from .lib.server import create_server
from .lib.singleton import Singleton

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable

    # Component callback types
    Callback = Callable[['Component'], Any]
    ErrorCallback = Callable[[Exception], Any]


class Component(metaclass=Singleton):
    """KUSANAGI SDK component class."""

    def __init__(self):
        # Private
        self.__resources = {}
        self.__startup = None
        self.__shutdown = None
        self.__error = None
        self.__logger = Logger(__name__)

        # Protected
        self._callbacks = {}

    def has_resource(self, name) -> bool:
        """
        Check if a resource name exist.

        :param name: Name of the resource.

        """

        return name in self.__resources

    def set_resource(self, name: str, factory: Callback):
        """
        Store a resource.

        Callback receives the `Component` instance as first argument.

        :param name: Name of the resource.
        :param factory: A callable that returns the resource value.

        :raises: ValueError

        """

        value = factory(self)
        if value is None:
            raise ValueError(f'Invalid result value for resource "{name}"')

        self.__resources[name] = value

    def get_resource(self, name: str) -> Any:
        """
        Get a resource.

        :param name: Name of the resource.

        :raises: LookupError

        """

        if not self.has_resource(name):
            raise LookupError(f'Resource "{name}" not found')

        return self.__resources[name]

    def startup(self, callback: Callback) -> Component:
        """
        Register a callback to be called during component startup.

        :param callback: A callback to execute on startup.

        """

        self.__startup = callback
        return self

    def shutdown(self, callback: Callback) -> Component:
        """
        Register a callback to be called during component shutdown.

        :param callback: A callback to execute on shutdown.

        """

        self.__shutdown = callback
        return self

    def error(self, callback: ErrorCallback) -> Component:
        """
        Register a callback to be called on error.

        :param callback: A callback to execute when the component fails to handle a request.

        """

        self.__error = callback
        return self

    def log(self, value: Any, level: int = INFO) -> Component:
        """
        Write a value to KUSANAGI logs.

        Given value is converted to string before being logged.

        Output is truncated to have a maximum of 100000 characters.

        :param value: The value to log.
        :param level: An optional log level to use for the log message.

        """

        self.__logger.log(level, value_to_log_string(value))
        return self

    def run(self) -> bool:
        """Run the SDK component."""

        # Create a helper to process component events
        events = Events(self.__startup, self.__shutdown, self.__error)

        # Run the server and check if all the callbacks run successfully
        success = False
        if events.startup(self):
            try:
                server = create_server(self, self._callbacks, events.error)
                server.start()
            except Exception as exc:
                self.__logger.exception(f'Component error: {exc}')
            else:
                success = True

        # Return False when shutdown fails otherwise use the success value
        return success if events.shutdown(self) else False
