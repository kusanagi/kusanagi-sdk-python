# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import asyncio
import errno
import os
import signal
from typing import TYPE_CHECKING

import zmq

from ..action import Action
from ..request import Request
from ..response import Response
from . import cli
from .asynchronous import AsyncAction
from .asynchronous import AsyncRequest
from .asynchronous import AsyncResponse
from .error import KusanagiError
from .logging import Logger
from .logging import setup_kusanagi_logging
from .msgpack import pack
from .msgpack import unpack
from .payload.command import CommandPayload
from .payload.error import ErrorPayload
from .payload.mapping import MappingPayload
from .payload.reply import ReplyPayload
from .state import State

if TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import List
    from typing import Union

    from ..api import Api
    from ..middleware import Middleware
    from ..service import Service
    from .payload.transport import TransportPayload

    ComponentType = Union[Middleware, Service]
    ApiType = Union[
        Request,
        Response,
        Action,
        AsyncRequest,
        AsyncResponse,
        AsyncAction,
    ]

# Constants for response meta
EMPTY_META = b'\x00'
SE = SERVICE_CALL = b'\x01'
FI = FILES = b'\x02'
TR = TRANSACTIONS = b'\x03'
DL = DOWNLOAD = b'\x04'

# Allowed response meta values
META_VALUES = (EMPTY_META, SE, FI, TR, DL)


def create_error_stream(rid: str, message: str) -> List[bytes]:
    """
    Create a new multipart error stream.

    :param rid: A request ID.
    :param message: The error message.

    """

    return [rid.encode('utf8'), EMPTY_META, pack(ErrorPayload.new(message=message))]


def initialize_logging(values):  # pragma: no cover
    component_type = values.get_component()
    name = values.get_name()
    version = values.get_version()
    framework_version = values.get_framework_version()
    level = values.get_log_level()
    setup_kusanagi_logging(component_type, name, version, framework_version, level)


def create_server(*args, **kwargs) -> Server:
    """
    Server factory.

    CLI argument values are parsed when calling this function.

    """

    # Update the global SDK debug state
    values = cli.parse_args()
    cli.DEBUG = values.is_debug()
    # Initialize the SDK logging
    initialize_logging(values)
    # Create a new server instace
    return Server(*args, values=values, **kwargs)


class Server(object):
    """SDK component server."""

    def __init__(self, component: ComponentType, callbacks: dict, on_error: Callable, values: cli.Input = None):
        """
        Constructor.

        :param component: The framework component being run.
        :param callbacks: The callbacks to call to handle each requests.
        :param on_error: The component error callback.
        :param values: Optional CLI input values.

        """

        self.__logger = Logger(__name__)
        self.__component = component
        self.__on_error = on_error
        self.__callbacks = callbacks
        self.__values = values
        self.__schemas = MappingPayload()
        self.__loop = asyncio.get_event_loop()
        self.__loop.add_signal_handler(signal.SIGTERM, self.stop)
        self.__loop.add_signal_handler(signal.SIGINT, self.stop)

    def __update_schemas(self, rid: str, stream: bytes):
        """
        Update schemas with new service schemas.

        :param rid: The ID of the current request.
        :param stream: A stream with the serialized mappings schemas.

        """

        self.__logger.debug('Updating schemas for Services ...', rid=rid)
        try:
            # NOTE: The msgpack unpack function can return many type of exceptions
            schemas = unpack(stream)
        except asyncio.CancelledError:  # pragma: no cover
            # Async task canceled during unpack
            raise
        except Exception as exc:  # pragma: no cover
            self.__logger.error(f'Failed to update schemas: Stream format is not valid: {exc}', rid=rid)

        try:
            self.__schemas = MappingPayload(schemas)
        except TypeError:  # pragma: no cover
            self.__logger.error('Failed to update schemas: The schema is not a dictionary', rid=rid)

    def __process_response(self, result: Any, state: State) -> List[bytes]:
        flags = EMPTY_META
        if isinstance(result, Request):
            payload = state.context['reply'].for_request()
        elif isinstance(result, Response):
            payload = state.context['reply'].for_response()
        elif isinstance(result, Action):
            payload: ReplyPayload = state.context['reply']
            transport: TransportPayload = payload.get_transport()
            if transport:
                flags = b''
                if transport.has_calls(result.get_name(), result.get_version()):
                    flags += SERVICE_CALL

                if transport.has_files():
                    flags += FILES

                if transport.has_transactions():
                    flags += TRANSACTIONS

                if transport.has_download():
                    flags += DOWNLOAD

                if not flags:
                    flags = EMPTY_META
        else:  # pragma: no cover
            self.__logger.error(f'Callback returned an invalid value: {result.__class__}')
            payload = ErrorPayload.new(message='Invalid value returned from callback')

        return [state.id.encode('utf8'), flags, pack(payload)]

    def __handle_callback_error(self, exc: Exception, api: Api, state: State) -> Union[Response, Action]:
        if isinstance(api, Action):
            action = Action(self.__component, state)
            action.error(str(exc), status='500 Internal Server Error')
            return action
        else:
            # The api is either a request or a response, and in both cases a new error response is returned
            response = Response(self.__component, state)
            http_response = response.get_http_response()
            http_response.set_status(500, 'Internal Server Error')
            http_response.set_body(str(exc))
            return response

    def __create_component(self, state: State, is_async: bool) -> ApiType:
        # Prepare the initial payload to use for the reply.
        # The action names for request and response middlewares are fixed, while services can have any action name.
        command = state.context['command']
        if state.values.get_component() == 'service':
            state.context['reply'] = ReplyPayload.new_action_reply(command)
            # When the callback is async use an Action component that support asyncio
            if is_async:
                api = AsyncAction(self.__component, state)
            else:
                api = Action(self.__component, state)
        elif state.action == 'request':
            # NOTE: The Request component can return a Request or a Response. The reply payload is initially defined
            #       as a request, but it is changed to a ResponsePayload when user calls Request.set_response().
            state.context['reply'] = ReplyPayload.new_request_reply(command)
            if is_async:
                api = AsyncRequest(self.__component, state)
            else:
                api = Request(self.__component, state)
        elif state.action == 'response':
            state.context['reply'] = ReplyPayload.new_response_reply(command)
            if is_async:
                api = AsyncResponse(self.__component, state)
            else:
                api = Response(self.__component, state)

        return api

    async def __process_action(self, state: State) -> List[bytes]:
        # Get the userland callback that processes the request
        callback = self.__callbacks[state.action]
        is_async_callback = asyncio.iscoroutinefunction(callback)

        # Execute the userland callback and if there is an error duting
        # its execution call the error callback of the component.
        api = self.__create_component(state, is_async_callback)
        try:
            if is_async_callback:
                result = await callback(api)
            else:
                # Run non async callbacks in the default executor
                result = await self.__loop.run_in_executor(None, callback, api)
        except asyncio.CancelledError:  # pragma: no cover
            # The task was canceled
            raise
        except KusanagiError as err:
            self.__logger.exception(f'Callback error: {err}')
            self.__on_error(err)

            # Any KusanagiError class is handled as a valid framework response.
            # Depending on the running component the result is a response or an action with an error.
            result = self.__handle_callback_error(err, api, state)
        except Exception as exc:
            self.__logger.exception(f'Callback error: {exc}')
            self.__on_error(exc)

            # Return an error payload when the callback fails with an exception
            payload = ErrorPayload.new(message=str(exc))
            return [state.id.encode('utf8'), EMPTY_META, pack(payload)]

        return self.__process_response(result, state)

    async def __process_request(self, state: State) -> List[bytes]:
        if state.schemas:
            self.__update_schemas(state.id, state.schemas)

        # Add service schemas to the state context
        state.context['schemas'] = self.__schemas

        # Return an error when action doesn't exist
        action = state.action
        if action not in self.__callbacks:
            title = state.get_component_title()
            return create_error_stream(state.id, f'Invalid action for component {title}: "{action}"')

        # Create the command payload using the request payload stream
        try:
            command = CommandPayload(unpack(state.payload))
        except asyncio.CancelledError:   # pragma: no cover
            # Async task canceled during unpack
            raise
        except Exception as exc:  # pragma: no cover
            msg = 'The request contains an invalid payload'
            self.__logger.critical(f'{msg}: {exc}', rid=state.id)
            return create_error_stream(state.id, msg)
        else:
            state.context['command'] = command

        return await self.__process_action(state)

    async def __handle_request(self, state: State) -> List[bytes]:
        # Process the request using the current execution timeout
        timeout = self.__values.get_timeout() / 1000.0  # seconds
        try:
            stream = await asyncio.wait_for(self.__process_request(state), timeout=timeout)
        except asyncio.TimeoutError:
            timeout_ms = timeout * 1000
            msg = f'Execution timed out after {timeout_ms}ms'
            pid = os.getpid()
            self.__logger.warning(f'{msg}. PID: {pid}', rid=state.id)
            # When the request times out return an error response
            stream = create_error_stream(state.id, msg)

        return stream

    async def listen(self):
        """
        Listen for incoming request.

        :raises: KusanagiError

        """

        self.__logger.debug('Creating the socket...')
        channel = self.__values.get_channel()
        try:
            ctx = zmq.asyncio.Context()
            socket = ctx.socket(zmq.REP)
            socket.bind(channel)
        except zmq.error.ZMQError as err:  # pragma: no cover
            if err.errno == errno.EADDRINUSE:
                socket_name = self.__values.get_socket()
                raise KusanagiError(f'Address unavailable: {socket_name}')
            elif err.errno == errno.EINTR:
                # The application is exiting during a blocking socket operation
                return

            raise KusanagiError(err.strerror)

        self.__logger.debug('Listening for incoming requests in channel: "%s"', channel)
        try:
            while True:
                event = await socket.poll()
                if event == zmq.POLLIN:
                    # Read the mulstipart stream
                    stream = await socket.recv_multipart()
                    # Parse the stream to create a state
                    state = State.create(self.__values, stream)
                    if state:
                        # Get a new stream with the response contents
                        stream = await self.__handle_request(state)
                    else:
                        # When the request format is not valid return a generic error response
                        stream = create_error_stream('-', 'Failed to handle request')

                    # Return the response contents to the client
                    await socket.send_multipart(stream)
        except zmq.error.ZMQError as err:  # pragma: no cover
            # The EINTR can happen when the application is exiting during a blocking
            # socket operation and it is not a critical error in this context.
            if err.errno != errno.EINTR:
                raise
        except asyncio.CancelledError:  # pragma: no cover
            pass
        finally:
            self.__logger.debug('Clossing the socket...')
            socket.close()

    def start(self):
        """Start the server."""

        self.__logger.debug('Using PID: %s', os.getpid())
        self.__logger.debug('Starting server...')
        try:
            self.__loop.run_until_complete(self.listen())
        except asyncio.CancelledError:  # pragma: no cover
            pass
        finally:  # pragma: no cover
            self.__logger.debug('Stopping the event loop...')
            self.__loop.stop()
            self.__loop.close()
            self.__logger.debug('Server stopped')

    def stop(self):  # pragma: no cover
        """Stop the server."""

        # Cancel all ongoing tasks before stopping the loop
        self.__logger.debug('Stopping the server...')
        error = None
        tasks = asyncio.Task.all_tasks()
        for task in tasks:
            # When an exception is found in a task save it
            if task.done() and task.exception() and not error:
                error = task.exception()
            else:
                task.cancel()

        # When an exception is found raise it
        if error:
            self.__logger.warning('Raising exception found while stopping tasks')
            raise error
