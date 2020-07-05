# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING

from .action import ActionSchema
from .lib.payload import ns
from .lib.payload.utils import payload_to_param

if TYPE_CHECKING:
    from typing import List

    from .lib.payload import Payload
    from .param import Param


class Callee(object):
    """Represents a callee service call info."""

    def __init__(self, payload: Payload):
        """
        Constructor.

        :param payload: The payload with the callee info.

        """

        self.__payload = payload

    def get_duration(self) -> int:
        """Get the duration of the call in milliseconds."""

        return self.__payload.get([ns.DURATION], 0)

    def is_remote(self) -> bool:
        """Check if the call is to a service in another Realm."""

        return self.__payload.exists([ns.GATEWAY])

    def get_address(self) -> str:
        """Get the remote gateway address."""

        return self.__payload.get([ns.GATEWAY], '')

    def get_timeout(self) -> int:
        """Get the timeout in milliseconds for the call to a service in another realm."""

        return self.__payload.get([ns.TIMEOUT], ActionSchema.DEFAULT_EXECUTION_TIMEOUT)

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__payload.get([ns.NAME], '')

    def get_version(self) -> str:
        """Get the service version."""

        return self.__payload.get([ns.VERSION], '')

    def get_action(self) -> str:
        """Get the name of the service action."""

        return self.__payload.get([ns.ACTION], '')

    def get_params(self) -> List[Param]:
        """
        Get the call parameters.

        An empty list is returned when there are no parameters defined for the call.

        """

        return [payload_to_param(payload) for payload in self.__payload.get([ns.PARAMS], [])]
