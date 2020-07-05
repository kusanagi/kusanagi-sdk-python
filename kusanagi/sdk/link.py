# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


class Link(object):
    """Represents a link object in the transport."""

    def __init__(self, address: str, name: str, ref: str, uri: str):
        """
        Constructor.

        :param address: The network address of the gateway>
        :param name: The name of the service.
        :param ref: The link reference.
        :param uri: The URI of the link.

        """

        self.__address = address
        self.__name = name
        self.__ref = ref
        self.__uri = uri

    def get_address(self) -> str:
        """Get the gateway address of the service."""

        return self.__address

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__name

    def get_link(self) -> str:
        """Get the link reference."""

        return self.__ref

    def get_uri(self) -> str:
        """Get the URI for the link."""

        return self.__uri
