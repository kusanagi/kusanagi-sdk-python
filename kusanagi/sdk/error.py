# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


class Error(Exception):
    """Represents an error object in the transport."""

    DEFAULT_MESSAGE = 'Unknown error'
    DEFAULT_CODE = 0
    DEFAULT_STATUS = '500 Internal Server Error'

    def __init__(
        self,
        address: str,
        name: str,
        version: str,
        message: str = DEFAULT_MESSAGE,
        code: int = DEFAULT_CODE,
        status: str = DEFAULT_STATUS,
    ):
        """
        Constructor.

        :param address: The network address of the gateway.
        :param name: The name of the service.
        :param version: The version of the service.
        :param message: An optional error message.
        :param code: An optional code for the error.
        :param status: An optional status text for the error.

        """

        self.__address = address
        self.__name = name
        self.__version = version
        self.__message = message
        self.__code = code
        self.__status = status

    def __str__(self):
        message = self.get_message()
        return f'[{self.__address}] {self.__name} ({self.__version}) error: {message}'

    def get_address(self) -> str:
        """Get the gateway address of the service."""

        return self.__address

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__name

    def get_version(self) -> str:
        """Get the service version."""

        return self.__version

    def get_message(self) -> str:
        """Get the error message."""

        return self.__message or self.DEFAULT_MESSAGE

    def get_code(self) -> int:
        """Get the error code."""

        return self.__code or self.DEFAULT_CODE

    def get_status(self) -> str:
        """Get the status text for the error."""

        return self.__status or self.DEFAULT_STATUS
