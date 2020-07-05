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
from .utils import file_to_payload
from .utils import param_to_payload

if TYPE_CHECKING:
    from typing import List

    from ...file import File
    from ...param import Param
    from .transport import TransportPayload


class CommandPayload(Payload):
    """Handles operations on command payloads."""

    path_prefix = [ns.COMMAND, ns.ARGUMENTS]

    @classmethod
    def new(cls, name: str, scope: str, args: dict = None) -> CommandPayload:
        """
        Create a command payload.

        :param name: The name of the command to call.
        :param scope: The type of component making the request.
        :param args: Optional command arguments.

        """

        p = cls({
            ns.COMMAND: {
                ns.NAME: name,
            },
            ns.META: {
                ns.SCOPE: scope,
            },
        })

        if args:
            p.set([ns.COMMAND, ns.ARGUMENTS], args, prefix=False)

        return p

    @classmethod
    def new_runtime_call(
        cls,
        caller_action: str,
        callee_service: str,
        callee_version: str,
        callee_action: str,
        params: List[Param] = None,
        files: List[File] = None,
        transport: TransportPayload = None,
    ) -> CommandPayload:
        """
        Create a command payload for a run-time call.

        :param caller_action:  The caller action.
        :param callee_service: The called service.
        :param callee_version: The called version.
        :param callee_action: The called action.
        :param params: Optional parameters to send.
        :param files: Optional files to send.
        :param transport: Optional transport payload.

        """

        args = {
            ns.ACTION: caller_action,
            ns.CALLEE: [callee_service, callee_version, callee_action],
            ns.TRANSPORT: transport or {},
        }

        if params:
            args[ns.PARAMS] = [param_to_payload(p) for p in params]

        if files:
            args[ns.FILES] = [file_to_payload(f) for f in files]

        return cls.new('runtime-call', 'service', args=args)

    def get_name(self) -> str:
        """Get the name of the command."""

        return self.get([ns.COMMAND, ns.NAME], '', prefix=False)

    def get_attributes(self) -> dict:
        """Get the attributes."""

        return self.get([ns.ATTRIBUTES], {})

    def get_service_call_data(self) -> dict:
        """Get the service call data."""

        return self.get([ns.CALL], {})

    def get_transport_data(self) -> dict:
        """Get the transport data."""

        return self.get([ns.TRANSPORT], {})

    def get_response_data(self) -> dict:
        """Get the response data."""

        return self.get([ns.RESPONSE], {})

    def get_request_id(self) -> str:
        """Get current request ID."""

        # The ID is available for request, response and action commands.
        # Request and response payloads have a meta argument with the ID.
        # Action have the ID in the transport meta instead.
        rid = self.get([ns.META, ns.ID], '')
        if not rid:
            rid = self.get([ns.TRANSPORT, ns.META, ns.ID], '')

        return rid
