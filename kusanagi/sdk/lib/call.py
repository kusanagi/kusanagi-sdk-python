# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import asyncio
import re
import time
from typing import TYPE_CHECKING

import zmq
import zmq.asyncio

from .error import KusanagiError
from .logging import RequestLogger
from .msgpack import pack
from .msgpack import unpack
from .payload import ns
from .payload.command import CommandPayload
from .payload.error import ErrorPayload
from .payload.reply import ReplyPayload
from .payload.transport import TransportPayload

if TYPE_CHECKING:
    from typing import Any
    from typing import List
    from typing import Tuple

    from .file import File
    from .param import Param

# Regexp to parse the addresses to be used as IPC names
IPC_RE = re.compile(r'[^a-zA-Z0-9]{1,}')

# Create a global ZMQ context for the run-time calls
CONTEXT = zmq.asyncio.Context()
CONTEXT.linger = 0

# Frame data to use for the run-time call multipart messages
RUNTIME_CALL = b'\x01'


def ipc(*args) -> str:
    """Create an IPC connection string."""

    name = IPC_RE.sub('-', '-'.join(args))
    return f'ipc://@kusanagi-{name}'


class CallError(KusanagiError):
    """Error raised when when run-time call fails."""

    def __init__(self, message: Any):
        super().__init__(f'Run-time call failed: {message}')


class AsyncClient(object):
    """Run-time service call client."""

    def __init__(self, logger: RequestLogger, tcp: bool = False):
        """
        Constructor.

        :param logger: A request logger.
        :param tcp: Optional flag to use TCP instead of IPC.

        """

        self.__logger = logger
        self.__tcp = tcp
        self.__duration = 0

    def get_duration(self) -> int:
        """Get the duration of the last call in milliseconds."""

        return round(self.__duration) if self.__duration is not None else 0

    async def call(
        self,
        address: str,
        action: str,
        callee: List[str],
        timeout: int,
        transport: TransportPayload,
        params: List[Param] = None,
        files: List[File] = None,
    ) -> Tuple[Any, TransportPayload]:
        """
        Make a Service run-time call.

        :param address: Caller Service address.
        :param action: The caller action name.
        :param callee: The callee Service name, version and action name.
        :param timeout: Timeout in milliseconds.
        :param transport: A transport payload.
        :param params: Optional list of parameters.
        :param files: Optional list of files.

        :raises: ValueError, KusanagiError, CallError

        """

        if transport is None:
            raise ValueError('Transport is required to make run-time calls')

        # Create the command payload for the call
        command = CommandPayload.new_runtime_call(
            action,
            callee[0],
            callee[1],
            callee[2],
            params=params,
            files=files,
            transport=transport,
        )

        # NOTE: Run-time calls are made to the server address where the caller is runnning
        #       and NOT directly to the service we wish to call. The KUSANAGI framework
        #       takes care of the call logic for us to keep consistency between all the SDKs.
        channel = f'tcp://{address}' if self.__tcp else ipc(address)
        socket = CONTEXT.socket(zmq.REQ)
        stream = None
        start = time.time()
        try:
            socket.connect(channel)
            await socket.send_multipart([RUNTIME_CALL, pack(command)], zmq.NOBLOCK)
            event = await socket.poll(timeout)
            if event == zmq.POLLIN:
                stream = await socket.recv()
            else:
                raise TimeoutError()
        except asyncio.CancelledError:  # pragma: no cover
            raise
        except TimeoutError:
            self.__logger.error(f'Run-time call to address "{address}" failed: Timeout')
            raise CallError('Timeout')
        except Exception as exc:
            self.__logger.error(f'Run-time call to address "{address}" failed: {exc}')
            raise CallError('Failed to make the request')
        finally:
            # Update the call duration in milliseconds
            self.__duration = (time.time() - start) * 1000
            if not socket.closed:
                socket.disconnect(channel)
                socket.close()

        # Parse the response stream
        try:
            payload = unpack(stream)
        except asyncio.CancelledError:  # pragma: no cover
            # Async task canceled during unpack
            raise
        except Exception as exc:
            self.__logger.error(f'Run-time call response format is invalid: {exc}')
            raise CallError('The response format is invalid')

        # Check that the response is a dictionary
        if not isinstance(payload, dict):
            self.__logger.error(f'Run-time call response data is not a dictionary')
            raise CallError('The payload data is not valid')

        # Check if the payload is an error payload, and if so use to raise an error
        if isinstance(payload, dict) and ns.ERROR in payload:
            error = ErrorPayload(payload)
            raise CallError(error.get_message())

        reply = ReplyPayload(payload)
        return (reply.get_return_value(), reply.get_transport())


class Client(AsyncClient):
    """Run-time service call client for non async contexts."""

    def call(self, *args, **kwargs):
        return asyncio.run(super().call(*args, **kwargs))
