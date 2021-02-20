# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import asyncio

import pytest


def test_async_action_calls_runtime(AsyncMock, mocker, state, schemas, action_reply):
    from kusanagi.sdk import AsyncAction
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    # Create a transport that is the returned by the call
    transport = TransportPayload()
    # Mock the call client to return the custom transport and return value
    client = mocker.Mock()
    client.get_duration.return_value = 123
    client.call = AsyncMock(return_value=[42, transport])
    mocker.patch('kusanagi.sdk.lib.asynchronous.AsyncClient', return_value=client)

    state.context['schemas'] = schemas
    state.context['command'] = CommandPayload()
    state.context['reply'] = action_reply
    params = [Param('foo')]
    files = [File('foo')]
    files[0].is_local = mocker.Mock(return_value=True)

    action = AsyncAction(Service(), state)

    # Mock the schemas
    schema = mocker.Mock()
    action.get_service_schema = mocker.Mock(return_value=schema)
    action_schema = mocker.Mock()
    schema.get_action_schema = mocker.Mock(return_value=action_schema)

    schema.has_file_server.return_value = True
    action_schema.has_return.return_value = True
    action_schema.has_call.return_value = True

    path = [ns.CALLS, action.get_name(), action.get_version()]
    assert not action._transport.exists(path)
    assert asyncio.run(action.call('baz', '1.0.0', 'blah', params, files, 1000)) == 42
    assert transport.get(path) == action._transport.get(path) == [{
        ns.NAME: 'baz',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.TIMEOUT: 1000,
        ns.DURATION: 123,
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: '',
            ns.TYPE: Param.TYPE_STRING,
        }],
        ns.FILES: [{
            ns.NAME: 'foo',
            ns.PATH: '',
            ns.MIME: '',
            ns.FILENAME: '',
            ns.SIZE: 0,
        }],
    }]

    # Call must fail when there is no file server and a local file is used
    schema.has_file_server.return_value = False
    with pytest.raises(KusanagiError):
        asyncio.run(action.call('baz', '1.0.0', 'blah', files=files))

    # The remote action must define a return value
    action_schema.has_return.return_value = False
    with pytest.raises(KusanagiError):
        asyncio.run(action.call('baz', '1.0.0', 'blah'))

    # Call must fail when the call is not defined in the config
    action_schema.has_call.return_value = False
    with pytest.raises(KusanagiError):
        asyncio.run(action.call('baz', '1.0.0', 'blah'))

    # Call must fail when the schemas are not defined
    action.get_service_schema = mocker.Mock(side_effect=LookupError)
    with pytest.raises(KusanagiError):
        asyncio.run(action.call('baz', '1.0.0', 'blah'))
