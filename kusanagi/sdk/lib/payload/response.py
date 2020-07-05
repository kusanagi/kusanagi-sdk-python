# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Payload
from . import ns

if TYPE_CHECKING:
    from typing import Any

    from .reply import ReplyPayload


class HttpResponsePayload(Payload):
    """Handles operations on HTTP response payloads."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reply = None

    def set(self, path: list, value: Any) -> bool:
        result = super().set(path, value)
        if self._reply:
            self._reply.set([ns.RESPONSE] + path, value)

        return result

    def append(self, path: list, value: Any) -> bool:
        result = super().set(path, value)
        if self._reply:
            self._reply.append([ns.RESPONSE] + path, value)

        return result

    def set_reply(self, reply: ReplyPayload) -> HttpResponsePayload:
        """
        Set the reply payload.

        :param reply: The reply payload.

        """

        # Clear the reply payload
        self._reply = None
        # Update the response values
        response = reply.get([ns.RESPONSE], {})
        for name, value in response.items():
            self.set([name], value)

        self._reply = reply
        return self
