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
from .transport import TransportPayload

if TYPE_CHECKING:
    from typing import Any

    from .command import CommandPayload


class ReplyPayload(Payload):
    """Handles operations on command reply payloads."""

    HTTP_VERSION = '1.1'
    HTTP_STATUS_OK = '200 OK'

    path_prefix = [ns.COMMAND_REPLY, ns.RESULT]

    @classmethod
    def new_request_reply(cls, command: CommandPayload) -> ReplyPayload:
        """Create a new command reply for a request."""

        call = command.get_service_call_data()
        return cls({
            ns.COMMAND_REPLY: {
                ns.NAME: command.get_name(),
                ns.RESULT: {
                    ns.ATTRIBUTES: command.get_attributes(),
                    ns.CALL: {
                        ns.SERVICE: call.get(ns.SERVICE, ''),
                        ns.VERSION: call.get(ns.VERSION, ''),
                        ns.ACTION: call.get(ns.ACTION, ''),
                        ns.PARAMS: call.get(ns.PARAMS, []),
                    },
                    ns.RESPONSE: {
                        ns.VERSION: cls.HTTP_VERSION,
                        ns.STATUS: cls.HTTP_STATUS_OK,
                        ns.HEADERS: {'Content-Type': ['text/plain']},
                        ns.BODY: b'',
                    },
                }
            }
        })

    @classmethod
    def new_response_reply(cls, command: CommandPayload) -> ReplyPayload:
        """Create a new command reply for a response."""

        return cls({
            ns.COMMAND_REPLY: {
                ns.NAME: command.get_name(),
                ns.RESULT: {
                    ns.ATTRIBUTES: command.get_attributes(),
                    ns.RESPONSE: command.get_response_data(),
                }
            }
        })

    @classmethod
    def new_action_reply(cls, command: CommandPayload) -> ReplyPayload:
        """
        Create a new command reply for a service action call.

        :param command: The command payload.

        """

        return cls({
            ns.COMMAND_REPLY: {
                ns.NAME: command.get_name(),
                ns.RESULT: {
                    ns.TRANSPORT: command.get_transport_data(),
                }
            }
        })

    def set_response(self, code: int, text: str) -> ReplyPayload:
        """
        Set a response in the payload.

        :param code: The HTTP status code for the response.
        :param text: The HTTP status text for the response.

        """

        self.set([ns.RESPONSE], {
            ns.VERSION: self.HTTP_VERSION,
            ns.STATUS: f'{code} {text}',
            ns.HEADERS: {},
            ns.BODY: b'',
        })
        return self

    def get_return_value(self) -> Any:
        """
        Get the return value if it exists.

        None is returned when there is no return value.

        """

        return self.get([ns.RETURN])

    def get_transport(self) -> TransportPayload:
        """
        Get the transport payload if it exists.

        None is returned when there is no transport data in the payload.

        """

        data = self.get([ns.TRANSPORT])
        return TransportPayload(data) if data else None

    def for_request(self) -> ReplyPayload:
        """Setup the reply for a request middleware."""

        self.delete([ns.RESPONSE])
        return self

    def for_response(self) -> ReplyPayload:
        """Setup the reply for a response middleware."""

        self.delete([ns.CALL])
        return self
