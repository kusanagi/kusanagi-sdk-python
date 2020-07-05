# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import logging
from typing import List
from typing import Optional

from . import cli
from .logging import RequestLogger

LOG = logging.getLogger(__name__)


class State(object):
    """State contains the data for a multipart request of the framework."""

    def __init__(self, values: cli.Input, stream: List[bytes]):
        """
        Constructor.

        :param values: The CLI input values.
        :param stream: The stream with the multipart data.

        :raises: ValueError

        """

        request_id, action, self.__schemas, self.__payload = stream
        self.__values = values
        self.__request_id = request_id.decode('utf8')
        self.__action = action.decode('utf8')
        self.__logger = RequestLogger('kusanagi', self.__request_id)
        # Context can be used to store any data related to the request
        self.context = {}

    @classmethod
    def create(cls, *args, **kwargs) -> Optional[State]:
        """
        Create a state from a multipart stream.

        None is returned when the stream is invalid.

        """

        try:
            return cls(*args, **kwargs)
        except ValueError as err:
            LOG.error(f'Received an invalid multipart request: {err}')

    @property
    def id(self) -> str:
        """Get the request ID."""

        return self.__request_id

    @property
    def action(self) -> str:
        """Get the action name."""

        return self.__action

    @property
    def schemas(self) -> bytes:
        """Get the service schemmas mapping data."""

        return self.__schemas

    @property
    def payload(self) -> bytes:
        """Get the request payload data."""

        return self.__payload

    @property
    def values(self) -> cli.Input:
        """Get the values for the CLI argument."""

        return self.__values

    @property
    def logger(self) -> RequestLogger:
        """Get the logger for the current request."""

        return self.__logger

    def get_component_title(self) -> str:
        """Get the title for the component."""

        return '"{}" ({})'.format(self.values.get_name(), self.values.get_version())
