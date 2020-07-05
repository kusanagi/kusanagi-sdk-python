# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import argparse
import inspect
import logging

from .call import ipc
from .logging import SYSLOG_NUMERIC

# This global is True when the SDK component is run in debug mode
DEBUG = False

# List of CLI options to run the SDK components
PARSER = argparse.ArgumentParser(allow_abbrev=False)
PARSER.add_argument(
    '-c', '--component',
    help='Component type.',
    required=True,
    choices=['service', 'middleware'],
)
PARSER.add_argument(
    '-D', '--debug',
    help='Enable component debug.',
    action='store_true',
)
PARSER.add_argument(
    '-L', '--log-level',
    help='Enable a logging using a numeric Syslog severity value to set the level.',
    type=int,
    choices=range(8),
)
PARSER.add_argument(
    '-n', '--name',
    help='Component name.',
    required=True,
)
PARSER.add_argument(
    '-p', '--framework-version',
    help='KUSANAGI framework version.',
    required=True,
)
PARSER.add_argument(
    '-s', '--socket',
    help='IPC socket name.',
)
PARSER.add_argument(
    '-t', '--tcp',
    help='TCP port to use when IPC socket is not used.',
    type=int,
)
PARSER.add_argument(
    '-T', '--timeout',
    help='Process execution timeout per request in milliseconds.',
    type=int,
    default=30000,
)
PARSER.add_argument(
    '-v', '--version',
    help='Component version.',
    required=True,
)
PARSER.add_argument(
    '-V', '--var',
    help='Component variables.',
    action='append',
    default=[],
)


def parse_args() -> Input:
    """Parse CLI argument values."""

    # Get the name of the current script
    caller_frame = inspect.getouterframes(inspect.currentframe())[-1]
    source_file = caller_frame[1]
    # Use the name as program name for the parser
    PARSER.prog = source_file
    # Get the CLI values
    values = vars(PARSER.parse_args())
    values['var'] = parse_key_value_list(values['var'])
    return Input(source_file, **values)


def parse_key_value_list(values: list) -> dict:
    """
    Option callback to validate a list of key/value arguments.

    Converts 'NAME=VALUE' CLI parameters to a dictionary.

    :raises: ValueError

    """

    if not values:
        return {}

    params = {}
    for value in values:
        parts = value.split('=', 1)
        if len(parts) != 2:
            raise ValueError('Invalid parameter format')

        param_name, param_value = parts
        params[param_name] = param_value

    return params


class Input(object):
    """CLI input values."""

    def __init__(self, path: str, **kwargs):
        """
        Constructor.

        The keywords are used as the input values dictionary.

        :param path: Path to the file being executed.

        """
        self.__path = path
        self.__values = kwargs

    def get_path(self) -> str:
        """
        Get the path to the file being executed.

        The path includes the file name.

        """

        return self.__path

    def get_component(self) -> str:
        """Get the component type."""

        return self.__values['component']

    def get_name(self) -> str:
        """Get the component name."""

        return self.__values['name']

    def get_version(self) -> str:
        """Get the component version."""

        return self.__values['version']

    def get_framework_version(self) -> str:
        """Get the KUSANAGI framework version."""

        return self.__values['framework_version']

    def get_socket(self) -> str:
        """Get the ZMQ socket name."""

        if self.is_tcp_enabled():
            return ''

        if not self.__values['socket']:
            # Create a default name for the socket when no name is available.
            # The 'ipc://' prafix is removed from the string to get the socket name.
            return ipc(self.get_component(), self.get_name(), self.get_version())[6:]
        else:
            return self.__values['socket']

    def get_tcp(self) -> int:
        """
        Get the port to use for TCP connections.

        Zero is returned when there is no TCP port assigned.

        """

        return self.__values['tcp'] or 0

    def is_tcp_enabled(self) -> bool:
        """Check if TCP connections should be used instead of IPC."""

        return self.get_tcp() != 0

    def get_channel(self) -> str:
        """Get the ZMQ channel to use for listening incoming requests."""

        if self.is_tcp_enabled():
            port = self.get_tcp()
            return f'tcp://127.0.0.1:{port}'
        else:
            # NOTE: The socket name already contains the "@kusanagi" prefix
            socket_name = self.get_socket()
            return f'ipc://{socket_name}'

    def get_timeout(self) -> int:
        """Get the process execution timeout in milliseconds."""

        return self.__values['timeout']

    def is_debug(self) -> bool:
        """Check if debug is enabled."""

        return self.__values['debug']

    def has_variable(self, name: str) -> bool:
        """
        Check if an engine variable is defined.

        :param name: The name of the variable.

        """

        return name in self.__values['var']

    def get_variable(self, name: str) -> str:
        """
        Get the value for an engine variable.

        An empty string is returned when the variable is not defined.

        :param name: The name of the variable.

        """

        return self.__values['var'].get(name, '')

    def get_variables(self) -> dict:
        """Get all the engine variables."""

        return dict(self.__values['var'])

    def has_logging(self) -> bool:
        """Check if logging is enabled."""

        return self.__values['log_level'] is not None

    def get_log_level(self) -> int:
        """Get the log level."""

        return SYSLOG_NUMERIC.get(self.__values['log_level'], logging.INFO)
