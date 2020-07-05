# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import TYPE_CHECKING
from typing import List

from .lib.payload import Payload
from .lib.payload import ns
from .lib.payload.utils import payload_to_param

if TYPE_CHECKING:
    from .param import Param


class Transaction(object):
    """Represents a transaction object in the transport."""

    TYPE_COMMIT = 'commit'
    TYPE_ROLLBACK = 'rollback'
    TYPE_COMPLETE = 'complete'
    TYPE_CHOICES = (TYPE_COMMIT, TYPE_ROLLBACK, TYPE_COMPLETE)

    def __init__(self, type_: str, payload: dict):
        """
        Constructor.

        The supported types are "commit", "rollback" or "complete".

        :param type_: The transaction type.
        :param payload: The payload data with the transaction info.

        :raises: TypeError

        """

        if type_ not in (self.TYPE_COMMIT, self.TYPE_ROLLBACK, self.TYPE_COMPLETE):
            raise TypeError(f'Invalid transaction type: "{type_}"')

        self.__type = type_
        self.__payload = Payload(payload)

    def get_type(self) -> str:
        """Get the transaction type."""

        return self.__type

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__payload.get([ns.NAME], '')

    def get_version(self) -> str:
        """Get the service version."""

        return self.__payload.get([ns.VERSION], '')

    def get_caller_action(self) -> str:
        """Get the name of the service action that registered the transaction."""

        return self.__payload.get([ns.CALLER], '')

    def get_callee_action(self) -> str:
        """Get the name of the action to be called by the transaction."""

        return self.__payload.get([ns.ACTION], '')

    def get_params(self) -> List['Param']:
        """
        Get the transaction parameters.

        An empty list is returned when there are no parameters defined for the transaction.

        """

        return [payload_to_param(payload) for payload in self.__payload.get([ns.PARAMS], [])]
