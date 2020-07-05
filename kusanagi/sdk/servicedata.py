# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import List

from .actiondata import ActionData


class ServiceData(object):
    """Represents a service which stored data in the transport."""

    def __init__(self, address: str, name: str, version: str, actions: dict):
        """
        Constructor.

        :param address: The network address of the gateway.
        :param name: The service name.
        :param version: The version of the service.
        :param actions: Transport data for the calls made to service.

        """

        self.__address = address
        self.__name = name
        self.__version = version
        self.__actions = actions

    def get_address(self) -> str:
        """Get the gateway address of the service."""

        return self.__address

    def get_name(self) -> str:
        """Get the service name."""

        return self.__name

    def get_version(self) -> str:
        """Get the service version."""

        return self.__version

    def get_actions(self) -> List[ActionData]:
        """
        Get the list of action data items for current service.

        Each item represents an action on the service for which data exists.

        """

        return [ActionData(name, data) for name, data in self.__actions.items()]
