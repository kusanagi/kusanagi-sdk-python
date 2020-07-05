# Python SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

from typing import TYPE_CHECKING

from .component import Component

if TYPE_CHECKING:
    from typing import Awaitable
    from typing import Callable
    from typing import Union

    from .request import Request
    from .response import Response

    # Types for the request
    RequestResult = Union[Request, Response]
    AsyncRequestCallback = Callable[[Request], Awaitable[RequestResult]]
    RequestCallback = Callable[[Request], RequestResult]
    # Types for the response
    AsyncResponseCallback = Callable[[Response], Awaitable[Response]]
    ResponseCallback = Callable[[Response], Response]


class Middleware(Component):
    """KUSANAGI middleware component."""

    def request(self, callback: Union[RequestCallback, AsyncRequestCallback]) -> Middleware:
        """
        Set a callback for requests.

        :param callback: Callback to handle requests.

        """

        self._callbacks['request'] = callback
        return self

    def response(self, callback: Union[ResponseCallback, AsyncResponseCallback]) -> Middleware:
        """
        Set callback for response.

        :param callback: Callback to handle responses.

        """

        self._callbacks['response'] = callback
        return self
