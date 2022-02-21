# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import asyncio

import pytest
import zmq


def test_lib_call_async_client_transport_required(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.logging import RequestLogger

    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    with pytest.raises(ValueError):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, None))


def test_lib_call_async_client_error_payload(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import CallError
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.payload.error import ErrorPayload

    payload = ErrorPayload.new()

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    # When an error payload is returned by the remote service it is used for the exception
    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    with pytest.raises(CallError, match=payload.get_message()):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, {}))


def test_lib_call_async_client_invalid_payload(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import CallError
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack

    payload = 'Boom !'

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    # When an error payload is returned by the remote service it is used for the exception
    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    with pytest.raises(CallError, match='payload data is not valid'):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, {}))


def test_lib_call_async_client_invalid_stream(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import CallError
    from kusanagi.sdk.lib.logging import RequestLogger

    stream = b'Boom !'

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=stream)
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    # When an error payload is returned by the remote service it is used for the exception
    client = AsyncClient(RequestLogger('kusanagi', 'RID'))

    with pytest.raises(CallError, match='response format is invalid'):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, {}))


def test_lib_call_async_client_timeout(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import CallError
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack({}))
    socket.poll = AsyncMock(return_value=0)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    # When an error payload is returned by the remote service it is used for the exception
    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    with pytest.raises(CallError, match='Timeout'):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, {}))


def test_lib_call_async_client_request_fail(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import CallError
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack({}))
    socket.poll = AsyncMock(side_effect=Exception)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    # When an error payload is returned by the remote service it is used for the exception
    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    with pytest.raises(CallError, match='Failed to make the request'):
        asyncio.run(client.call('1.2.3.4:77', 'foo', ['bar', '1.0.0', 'baz'], 1000, {}))


def test_lib_call_async_client_ipc(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.call import ipc
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    address = '1.2.3.4:77'
    channel = ipc(address)
    transport = {
        ns.META: {},
    }
    payload = ReplyPayload()
    payload.set([ns.RETURN], 42)
    payload.set([ns.TRANSPORT], transport)

    socket = mocker.Mock()
    socket.closed = False
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    client = AsyncClient(RequestLogger('kusanagi', 'RID'))
    return_value, transport = asyncio.run(client.call(address, 'foo', ['bar', '1.0.0', 'baz'], 1000, transport))
    assert return_value == 42
    assert transport == transport
    assert client.get_duration() >= 0
    socket.connect.assert_called_once_with(channel)
    socket.disconnect.assert_called_once_with(channel)
    socket.close.assert_called_once()


def test_lib_call_async_client_tcp(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import AsyncClient
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    address = '1.2.3.4:77'
    channel = f'tcp://{address}'
    transport = {
        ns.META: {},
    }
    payload = ReplyPayload()
    payload.set([ns.RETURN], 42)
    payload.set([ns.TRANSPORT], transport)

    socket = mocker.Mock()
    socket.closed = False
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    client = AsyncClient(RequestLogger('kusanagi', 'RID'), tcp=True)
    return_value, transport = asyncio.run(client.call(address, 'foo', ['bar', '1.0.0', 'baz'], 1000, transport))
    assert return_value == 42
    assert transport == transport
    assert client.get_duration() >= 0
    socket.connect.assert_called_once_with(channel)
    socket.disconnect.assert_called_once_with(channel)
    socket.close.assert_called_once()


def test_lib_call_client_ipc(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import Client
    from kusanagi.sdk.lib.call import ipc
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    address = '1.2.3.4:77'
    transport = {
        ns.META: {},
    }
    payload = ReplyPayload()
    payload.set([ns.RETURN], 42)
    payload.set([ns.TRANSPORT], transport)

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    client = Client(RequestLogger('kusanagi', 'RID'))
    return_value, transport = client.call(address, 'foo', ['bar', '1.0.0', 'baz'], 1000, transport)
    assert return_value == 42
    assert transport == transport
    socket.connect.assert_called_once_with(ipc(address))


def test_lib_call_client_tcp(AsyncMock, mocker, logs):
    from kusanagi.sdk.lib.call import Client
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.msgpack import pack
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    address = '1.2.3.4:77'
    transport = {
        ns.META: {},
    }
    payload = ReplyPayload()
    payload.set([ns.RETURN], 42)
    payload.set([ns.TRANSPORT], transport)

    socket = mocker.Mock()
    socket.send_multipart = AsyncMock()
    socket.recv = AsyncMock(return_value=pack(payload))
    socket.poll = AsyncMock(return_value=zmq.POLLIN)
    CONTEXT = mocker.patch('kusanagi.sdk.lib.call.CONTEXT')
    CONTEXT.socket.return_value = socket

    client = Client(RequestLogger('kusanagi', 'RID'), tcp=True)
    return_value, transport = client.call(address, 'foo', ['bar', '1.0.0', 'baz'], 1000, transport)
    assert return_value == 42
    assert transport == transport
    socket.connect.assert_called_once_with(f'tcp://{address}')
