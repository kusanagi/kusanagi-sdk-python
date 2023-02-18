# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import asyncio

import pytest
import zmq


def test_lib_server_create(mocker, input_):
    from kusanagi.sdk.lib.server import Server
    from kusanagi.sdk.lib.server import create_server

    mocker.patch('kusanagi.sdk.lib.cli.parse_args', return_value=input_)
    setup_kusanagi_logging = mocker.patch('kusanagi.sdk.lib.server.setup_kusanagi_logging')
    mocker.patch('kusanagi.sdk.lib.server.asyncio.get_event_loop')

    server = create_server(mocker.Mock(), {}, None)
    assert isinstance(server, Server)
    setup_kusanagi_logging.assert_called_once_with(
        input_.get_component(),
        input_.get_name(),
        input_.get_version(),
        input_.get_framework_version(),
        input_.get_log_level(),
    )


def test_lib_server_start(mocker, input_):
    from kusanagi.sdk.lib.server import Server

    loop = mocker.Mock()
    mocker.patch('kusanagi.sdk.lib.server.asyncio.get_event_loop', return_value=loop)
    server = Server(mocker.Mock(), {}, None, input_)
    server.listen = mocker.Mock(return_value='listen')
    server.start()
    server.listen.assert_called_once()
    loop.run_until_complete.assert_called_once_with('listen')
    loop.stop.assert_called_once()
    loop.close.assert_called_once()


def test_lib_server_stop(mocker, input_):
    from kusanagi.sdk.lib.server import Server

    mocker.patch('kusanagi.sdk.lib.server.asyncio.get_event_loop')
    task = mocker.Mock()
    all_tasks = mocker.patch('kusanagi.sdk.lib.server.asyncio.all_tasks')
    all_tasks.return_value = [task]
    server = Server(mocker.Mock(), {}, None, input_)

    # Unfinished tasks must be canceled
    task.done.return_value = False
    server.stop()
    task.done.assert_called_once()
    task.cancel.assert_called_once()

    # When there is an exception it must be raised
    task.done.return_value = True
    task.exception.return_value = Exception('Test')
    with pytest.raises(Exception, match='Test'):
        server.stop()


def test_lib_server_timeout(AsyncMock, mocker, logs, input_):
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.server import Server
    from kusanagi.sdk.lib.payload.error import ErrorPayload

    stream = [b'RID', b'foo', b'', pack({})]

    mocker.patch('kusanagi.sdk.lib.server.asyncio.get_event_loop')
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    server = Server(mocker.Mock(), {}, None, input_)
    server._Server__process_request = AsyncMock(side_effect=asyncio.TimeoutError)
    asyncio.run(server.listen())
    socket.close.assert_called_once()

    # Get the error payload from the response stream
    socket.send_multipart.assert_called_once()
    assert len(socket.send_multipart.call_args_list) == 1
    stream = socket.send_multipart.call_args[0][0]
    assert len(stream) == 3
    payload = ErrorPayload(unpack(stream[2]))
    assert payload.get_message().startswith('Execution timed out')


def test_lib_server_invalid_request_stream(AsyncMock, mocker, logs, input_):
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.server import Server
    from kusanagi.sdk.lib.payload.error import ErrorPayload

    mocker.patch('kusanagi.sdk.lib.server.asyncio.get_event_loop')
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=[])
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    server = Server(mocker.Mock(), {}, None, input_)
    asyncio.run(server.listen())
    socket.close.assert_called_once()

    # Get the error payload from the response stream
    socket.send_multipart.assert_called_once()
    assert len(socket.send_multipart.call_args_list) == 1
    stream = socket.send_multipart.call_args[0][0]
    assert len(stream) == 3
    payload = ErrorPayload(unpack(stream[2]))
    assert payload.get_message() == 'Failed to handle request'


@pytest.mark.asyncio
async def test_lib_server_middleware_request(AsyncMock, mocker, input_):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    command = CommandPayload()
    command.set([ns.CALL], {
        ns.SERVICE: 'foo',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'bar',
    })
    command.set([ns.COMMAND, ns.NAME], 'request', prefix=False)

    stream = [b'RID', b'request', pack({}), pack(command)]

    # Change the input values to return middleware as component
    input_.get_component = mocker.Mock(return_value='middleware')

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback = mocker.Mock(side_effect=lambda request: request)
    server = Server(Middleware(), {'request': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback.assert_called_once()
    args, _ = callback.call_args
    assert isinstance(args[0], Request)

    # Check that the result is a reply payload containing the call info
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    payload = unpack(stream[2])
    assert isinstance(payload, dict)
    reply = ReplyPayload(payload)
    assert reply.exists([ns.CALL])

    flags = stream[1]
    assert EMPTY_META == flags


@pytest.mark.asyncio
async def test_lib_server_middleware_request_response(AsyncMock, mocker, input_):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    command = CommandPayload()
    command.set([ns.CALL], {
        ns.SERVICE: 'foo',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'bar',
    })
    command.set([ns.COMMAND, ns.NAME], 'request', prefix=False)

    stream = [b'RID', b'request', pack({}), pack(command)]

    # Change the input values to return middleware as component
    input_.get_component = mocker.Mock(return_value='middleware')

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    # Instead of a request the middleware callback returns a response
    callback = mocker.Mock(side_effect=lambda request: request.new_response())

    server = Server(Middleware(), {'request': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback.assert_called_once()
    args, _ = callback.call_args
    assert isinstance(args[0], Request)

    # Check that the result is a reply payload containing the response
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    payload = unpack(stream[2])
    assert isinstance(payload, dict)
    reply = ReplyPayload(payload)
    assert reply.get([ns.RESPONSE, ns.STATUS]) == '200 OK'
    assert reply.get([ns.RESPONSE, ns.VERSION]) == '1.1'

    flags = stream[1]
    assert EMPTY_META == flags


@pytest.mark.asyncio
async def test_lib_server_middleware_response(AsyncMock, mocker, input_):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    command = CommandPayload()
    command.set([ns.RESPONSE], {
        ns.STATUS: '200 OK',
        ns.VERSION: '1.1',
    })
    command.set([ns.COMMAND, ns.NAME], 'response', prefix=False)

    stream = [b'RID', b'response', pack({}), pack(command)]

    # Change the input values to return middleware as component
    input_.get_component = mocker.Mock(return_value='middleware')

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback = mocker.Mock(side_effect=lambda response: response)
    server = Server(Middleware(), {'response': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback.assert_called_once()
    args, _ = callback.call_args
    assert isinstance(args[0], Response)

    # Check that the result is a reply payload containing the response
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    payload = unpack(stream[2])
    assert isinstance(payload, dict)
    reply = ReplyPayload(payload)
    assert reply.get([ns.RESPONSE, ns.STATUS]) == '200 OK'
    assert reply.get([ns.RESPONSE, ns.VERSION]) == '1.1'

    flags = stream[1]
    assert EMPTY_META == flags


@pytest.mark.asyncio
async def test_lib_server_service_action(AsyncMock, mocker, input_, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import DOWNLOAD
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import FILES
    from kusanagi.sdk.lib.server import SERVICE_CALL
    from kusanagi.sdk.lib.server import TRANSACTIONS
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'action', prefix=False)
    action_command.set([ns.TRANSPORT, ns.TRANSACTIONS], {})
    action_command.set([ns.TRANSPORT, ns.BODY], {})
    action_command.set([ns.TRANSPORT, ns.CALLS], {'foo': {'1.0.0': [{}]}})

    stream = [b'RID', b'action', pack({}), pack(action_command)]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback = mocker.Mock(side_effect=lambda action: action)
    server = Server(Service(), {'action': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback.assert_called_once()
    args, _ = callback.call_args
    assert isinstance(args[0], Action)

    # Check that the result is a reply payload containing the transport
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    reply = ReplyPayload(unpack(stream[2]))
    assert reply.exists([ns.TRANSPORT])

    flags = stream[1]
    assert EMPTY_META not in flags
    assert DOWNLOAD in flags
    assert FILES in flags
    assert SERVICE_CALL in flags
    assert TRANSACTIONS in flags


@pytest.mark.asyncio
async def test_lib_server_service_action_empty_transport_flags(AsyncMock, mocker, input_, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'action', prefix=False)
    action_command.delete([ns.TRANSPORT, ns.FILES])

    stream = [b'RID', b'action', pack({}), pack(action_command)]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback = mocker.Mock(side_effect=lambda action: action)
    server = Server(Service(), {'action': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback.assert_called_once()
    args, _ = callback.call_args
    assert isinstance(args[0], Action)

    # Check that the result is a reply payload containing the transport
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    reply = ReplyPayload(unpack(stream[2]))
    assert reply.exists([ns.TRANSPORT])

    flags = stream[1]
    assert EMPTY_META == flags


@pytest.mark.asyncio
async def test_lib_server_service_async_action(AsyncMock, mocker, input_, action_command):
    from kusanagi.sdk import AsyncAction
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'action', prefix=False)

    stream = [b'RID', b'action', pack({}), pack(action_command)]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback_mock = mocker.Mock()

    async def callback(action):
        callback_mock(action)
        return action

    server = Server(Service(), {'action': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was called with a Request instance
    callback_mock.assert_called_once()
    args, _ = callback_mock.call_args
    assert isinstance(args[0], AsyncAction)

    # Check that the result is a reply payload containing the transport
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    reply = ReplyPayload(unpack(stream[2]))
    assert reply.exists([ns.TRANSPORT])


@pytest.mark.asyncio
async def test_lib_server_invalid_request_action(AsyncMock, mocker, input_):
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload.error import ErrorPayload
    from kusanagi.sdk.lib.server import EMPTY_META
    from kusanagi.sdk.lib.server import Server

    stream = [b'RID', b'boom!', b'', pack({})]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    callback = mocker.Mock(side_effect=lambda component: component)
    server = Server(mocker.Mock(), {'action': callback}, None, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    # Check that the callback was not called
    callback.assert_not_called()

    # Check that the result is a reply payload containing the error
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    payload = ErrorPayload(unpack(stream[2]))
    assert payload.get_message().startswith('Invalid action for component')

    flags = stream[1]
    assert EMPTY_META == flags


@pytest.mark.asyncio
async def test_lib_server_middleware_callback_error(AsyncMock, mocker, input_, logs, action_command):
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Middleware
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'request', prefix=False)

    stream = [b'RID', b'request', pack({}), pack(action_command)]

    # Change the input values to return middleware as component
    input_.get_component = mocker.Mock(return_value='middleware')

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    # Define a custom KUSANAGI error to be raised from the callback
    error = KusanagiError('Test Error')

    on_error = mocker.Mock()
    callback = mocker.Mock(side_effect=error)
    server = Server(Middleware(), {'request': callback}, on_error, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    on_error.assert_called_once_with(error)

    # Check that the result is a reply payload containing an error response
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    reply = ReplyPayload(unpack(stream[2]))
    assert reply.get([ns.RESPONSE, ns.STATUS]) == '500 Internal Server Error'
    assert reply.get([ns.RESPONSE, ns.BODY]) == str(error)


@pytest.mark.asyncio
async def test_lib_server_service_callback_error(AsyncMock, mocker, input_, logs, action_command):
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'action', prefix=False)

    stream = [b'RID', b'action', pack({}), pack(action_command)]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    # Define a custom KUSANAGI error to be raised from the callback
    error = KusanagiError('Test Error')

    on_error = mocker.Mock()
    callback = mocker.Mock(side_effect=error)
    server = Server(Service(), {'action': callback}, on_error, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    on_error.assert_called_once_with(error)

    # Check that the result is a reply payload containing the transport
    # and inside the transport the custom error.
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    reply = ReplyPayload(unpack(stream[2]))
    address = reply.get([ns.TRANSPORT, ns.META, ns.GATEWAY])[1]
    errors = reply.get([ns.TRANSPORT, ns.ERRORS, address, 'foo', '1.0.0'])
    assert isinstance(errors, list)
    assert len(errors) == 1
    assert errors[0].get(ns.MESSAGE) == str(error)


@pytest.mark.asyncio
async def test_lib_server_component_callback_exception(AsyncMock, mocker, input_, logs, action_command):
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.msgpack import unpack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.error import ErrorPayload
    from kusanagi.sdk.lib.server import Server

    # Prepare a command payload for the request
    action_command.set([ns.COMMAND, ns.NAME], 'action', prefix=False)

    stream = [b'RID', b'action', pack({}), pack(action_command)]

    # Mock the ZMQ socket and use the "send_multipart" to stop
    # the server by raising the asyncio.CancelledError.
    socket = mocker.Mock()
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    socket.recv_multipart = AsyncMock(return_value=stream)
    socket.send_multipart = AsyncMock(side_effect=asyncio.CancelledError)
    context = mocker.Mock()
    context.socket.return_value = socket
    mocker.patch('zmq.asyncio.Context', return_value=context)

    # Define a generic exception
    error = Exception('Test Error')

    on_error = mocker.Mock()
    callback = mocker.Mock(side_effect=error)
    server = Server(Service(), {'action': callback}, on_error, input_)
    await server.listen()
    socket.close.assert_called_once()
    socket.send_multipart.assert_called_once()

    on_error.assert_called_once_with(error)

    # Check that the result is an error reply
    args, _ = socket.send_multipart.call_args
    stream = args[0]
    assert len(stream) == 3
    payload = ErrorPayload(unpack(stream[2]))
    assert payload.get_message() == str(error)
