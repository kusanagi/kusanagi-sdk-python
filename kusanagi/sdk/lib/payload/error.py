# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from . import Payload
from . import ns


class ErrorPayload(Payload):
    """Handles operations on error payloads."""

    DEFAULT_MESSAGE = 'Unknown error'
    DEFAULT_STATUS = '500 Internal Server Error'

    path_prefix = [ns.ERROR]

    @classmethod
    def new(cls, message: str = DEFAULT_MESSAGE, code: int = 0, status: str = DEFAULT_STATUS) -> ErrorPayload:
        return cls({
            ns.ERROR: {
                ns.MESSAGE: message,
                ns.CODE: code,
                ns.STATUS: status,
            }
        })

    def get_message(self) -> str:
        """Get the error message."""

        return self.get([ns.MESSAGE], self.DEFAULT_MESSAGE)

    def get_code(self) -> int:
        """Get the error code."""

        return self.get([ns.CODE], 0)

    def get_status(self) -> str:
        """Get the error status code."""

        return self.get([ns.STATUS], self.DEFAULT_STATUS)
