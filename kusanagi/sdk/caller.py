# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from .callee import Callee
from .lib.payload import Payload


class Caller(object):
    """Represents a service which registered call in the transport."""

    def __init__(self, name: str, version: str, action: str, callee: dict):
        """
        Constructor.

        :param name: The name of the service.
        :param version: The version of the service.
        :param action: The name of the action.
        :param calee: The payload data with the callee info.

        """

        self.__name = name
        self.__version = version
        self.__action = action
        self.__callee = Payload(callee)

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__name

    def get_version(self) -> str:
        """Get the service version."""

        return self.__version

    def get_action(self) -> str:
        """Get the name of the service action."""

        return self.__action

    def get_callee(self) -> Callee:
        """Get the callee info for the service being called."""

        return Callee(self.__callee)
