# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from typing import Union

    DataType = Union[dict, List[dict]]


class ActionData(object):
    """The ActionData class represents action data in the transport."""

    def __init__(self, name: str, data: List[DataType]):
        """
        Constructor.

        The data dan be a list where each item can be a list or a dictionary.
        An item that is a list means that a "collection" wad returned for that call,
        where and item that is a dictionary means that an "entity" was returned in
        that call.

        :param name: Name of the service action.
        :param data: Transport data for the calls made to the service action.

        """

        self.__name = name
        self.__data = data

    def get_name(self) -> str:
        """Get the name of the service action that returned the data."""

        return self.__name

    def is_collection(self) -> bool:
        """Checks if the data for this action is a collection."""

        return isinstance(self.__data[0], list)

    def get_data(self) -> List[DataType]:
        """Get the transport data for the service action."""

        # Copy the data to avoid indirect modification
        return copy.deepcopy(self.__data)
