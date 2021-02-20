# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import os

import pytest


def test_action_defaults(state):
    from kusanagi.sdk import Action
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    state.context['command'] = CommandPayload()
    state.context['reply'] = ReplyPayload()

    action = Action(Service(), state)
    assert not action.is_origin()
    assert action.get_action_name() == state.action
    assert not action.has_param('foo')

    param = action.get_param('foo')
    assert isinstance(param, Param)
    assert param.get_name() == 'foo'
    assert action.get_params() == []

    assert not action.has_file('foo')
    file = action.get_file('foo')
    assert isinstance(file, File)
    assert file.get_name() == 'foo'
    assert action.get_files() == []


def test_action(state, schemas, action_command, action_reply):
    from kusanagi.sdk import Action
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['schemas'] = schemas
    state.context['command'] = action_command
    state.context['reply'] = action_reply

    action = Action(Service(), state)
    assert action.is_origin()
    assert action.get_action_name() == state.action

    assert not action_reply.exists([ns.TRANSPORT, ns.META, ns.PROPERTIES, 'foo'])
    assert isinstance(action.set_property('foo', 'bar'), Action)
    assert action_reply.get([ns.TRANSPORT, ns.META, ns.PROPERTIES, 'foo']) == 'bar'
    # Property values can only be string
    with pytest.raises(TypeError):
        action.set_property('foo', 1)

    assert action.has_param('foo')
    param = action.get_param('foo')
    assert isinstance(param, Param)
    assert param.get_name() == 'foo'
    assert param.get_value() == 'bar'
    params = action.get_params()
    assert len(params) == 1
    assert params[0].get_name() == param.get_name()
    assert params[0].get_value() == param.get_value()
    assert params[0].get_type() == param.get_type()
    param = action.new_param('baz', 77, Param.TYPE_INTEGER)
    assert isinstance(param, Param)
    assert param.get_name() == 'baz'
    assert param.get_value() == 77
    assert param.get_type() == Param.TYPE_INTEGER
    assert param.exists()

    assert action.has_file('foo')
    file = action.get_file('foo')
    assert isinstance(file, File)
    assert file.get_name() == 'foo'
    files = action.get_files()
    assert len(files) == 1
    assert files[0].get_name() == file.get_name()


def test_action_download(DATA_DIR, mocker, state, schemas, action_command, action_reply):
    from kusanagi.sdk import Action
    from kusanagi.sdk import File
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['schemas'] = schemas
    state.context['command'] = action_command
    state.context['reply'] = action_reply

    action = Action(Service(), state)

    path = os.path.join(DATA_DIR, 'file.txt')
    file = action.new_file('baz', path, 'mime/custom')
    assert isinstance(file, File)
    assert file.get_name() == 'baz'
    assert file.get_path() == f'file://{path}'
    assert file.get_mime() == 'mime/custom'

    # Mock the schema to control the file server setting
    schema = mocker.Mock()
    action.get_service_schema = mocker.Mock(return_value=schema)

    # Download can't be assigned when the service doesn;t have a file server enabled
    schema.has_file_server.return_value = False
    with pytest.raises(LookupError):
        action.set_download(file)

    schema.has_file_server.return_value = True
    assert not action._transport.has_download()
    assert isinstance(action.set_download(file), Action)
    assert action._transport.has_download()
    assert action._transport.get([ns.BODY]).get(ns.NAME) == file.get_name()

    # Download values must be a file
    with pytest.raises(TypeError):
        action.set_download(1)


def test_action_return(mocker, state, schemas, action_reply):
    from kusanagi.sdk import Action
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Service
    from kusanagi.sdk.action import DEFAULT_RETURN_VALUES
    from kusanagi.sdk.lib import datatypes
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    state.context['schemas'] = schemas
    state.context['command'] = CommandPayload()
    state.context['reply'] = action_reply

    # Mock the schemas
    schema = mocker.Mock()
    Action.get_service_schema = mocker.Mock(return_value=schema)
    action_schema = mocker.Mock()
    action_schema.has_return.return_value = True
    action_schema.get_return_type.return_value = datatypes.TYPE_INTEGER
    schema.get_action_schema = mocker.Mock(return_value=action_schema)

    action = Action(Service(), state)

    assert action_reply.get([ns.RETURN]) == DEFAULT_RETURN_VALUES[datatypes.TYPE_INTEGER]
    assert action.set_return(42)
    assert action_reply.get([ns.RETURN]) == 42

    # Invalud return types should not be allowed
    action_schema.get_return_type.return_value = datatypes.TYPE_BOOLEAN
    with pytest.raises(KusanagiError):
        action.set_return(42)

    # Return value is not allowed when it is not supported by the action
    action_schema.has_return.return_value = False
    with pytest.raises(KusanagiError):
        action.set_return(42)

    # Call must fail when the schemas are not defined
    action.get_service_schema = mocker.Mock(side_effect=LookupError)
    with pytest.raises(KusanagiError):
        action.set_return(42)


def test_action_data_entity(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.DATA, address, action.get_name(), action.get_version(), action.get_action_name()]
    assert not action._transport.exists(path)
    assert isinstance(action.set_entity({'value': 1}), Action)
    assert action._transport.get(path) == [{'value': 1}]

    # Entity must be a dictionary
    with pytest.raises(TypeError):
        action.set_entity([])


def test_action_data_collection(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.DATA, address, action.get_name(), action.get_version(), action.get_action_name()]
    assert not action._transport.exists(path)
    assert isinstance(action.set_collection([{'value': 1}]), Action)
    assert action._transport.get(path) == [[{'value': 1}]]

    # Entity must be a list
    with pytest.raises(TypeError):
        action.set_collection({})

    # Entity must be a list of dicts
    with pytest.raises(TypeError):
        action.set_collection([1])


def test_action_relations_one(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.RELATIONS, address, 'foo', '1', address, 'bar']
    assert not action._transport.exists(path)
    assert isinstance(action.relate_one('1', 'bar', '2'), Action)
    assert action._transport.get(path) == '2'

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.relate_one('', 'bar', '2')

    with pytest.raises(ValueError):
        action.relate_one('1', '', '2')

    with pytest.raises(ValueError):
        action.relate_one('1', 'bar', '')


def test_action_relations_many(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.RELATIONS, address, 'foo', '1', address, 'bar']
    assert not action._transport.exists(path)
    assert isinstance(action.relate_many('1', 'bar', ['2', '3']), Action)
    assert action._transport.get(path) == ['2', '3']

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.relate_many('', 'bar', ['2'])

    with pytest.raises(ValueError):
        action.relate_many('1', '', ['2'])

    with pytest.raises(ValueError):
        action.relate_many('1', 'bar', [])

    # The foreign keys must be a list
    with pytest.raises(TypeError):
        action.relate_many('1', 'bar', '2')


def test_action_relations_one_remote(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    remote = 'http://6.6.6.6:77'
    path = [ns.RELATIONS, address, 'foo', '1', remote, 'bar']
    assert not action._transport.exists(path)
    assert isinstance(action.relate_one_remote('1', remote, 'bar', '2'), Action)
    assert action._transport.get(path) == '2'

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.relate_one_remote('', remote, 'bar', '2')

    with pytest.raises(ValueError):
        action.relate_one_remote('1', '', 'bar', '2')

    with pytest.raises(ValueError):
        action.relate_one_remote('1', remote, '', '2')

    with pytest.raises(ValueError):
        action.relate_one_remote('1', remote, 'bar', '')


def test_action_relations_many_remote(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    remote = 'http://6.6.6.6:77'
    path = [ns.RELATIONS, address, 'foo', '1', remote, 'bar']
    assert not action._transport.exists(path)
    assert isinstance(action.relate_many_remote('1', remote, 'bar', ['2', '3']), Action)
    assert action._transport.get(path) == ['2', '3']

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.relate_many_remote('', remote, 'bar', ['2', '3'])

    with pytest.raises(ValueError):
        action.relate_many_remote('1', '', 'bar', ['2', '3'])

    with pytest.raises(ValueError):
        action.relate_many_remote('1', remote, '', ['2', '3'])

    with pytest.raises(ValueError):
        action.relate_many_remote('1', remote, 'bar', [])

    # The foreign keys must be a list
    with pytest.raises(TypeError):
        action.relate_many_remote('1', remote, 'bar', '2')


def test_action_links(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.LINKS, address, action.get_name(), 'first']
    assert not action._transport.exists(path)
    assert isinstance(action.set_link('first', '/test'), Action)
    assert action._transport.get(path) == '/test'

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.set_link('', '/test')

    with pytest.raises(ValueError):
        action.set_link('first', '')


def test_action_transactions_commit(state):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    state.context['command'] = CommandPayload()
    params = [Param('foo', 'bar')]

    action = Action(Service(), state)
    path = [ns.TRANSACTIONS, TransportPayload.TRANSACTION_COMMIT]
    assert not action._transport.exists(path)
    assert isinstance(action.commit('bar', params), Action)
    assert action._transport.get(path) == [{
        ns.NAME: action.get_name(),
        ns.VERSION: action.get_version(),
        ns.CALLER: action.get_action_name(),
        ns.ACTION: 'bar',
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.TYPE: Param.TYPE_STRING,
            ns.VALUE: 'bar',
        }],
    }]

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.commit('')


def test_action_transactions_rollback(state):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    state.context['command'] = CommandPayload()
    params = [Param('foo', 'bar')]

    action = Action(Service(), state)
    path = [ns.TRANSACTIONS, TransportPayload.TRANSACTION_ROLLBACK]
    assert not action._transport.exists(path)
    assert isinstance(action.rollback('bar', params), Action)
    assert action._transport.get(path) == [{
        ns.NAME: action.get_name(),
        ns.VERSION: action.get_version(),
        ns.CALLER: action.get_action_name(),
        ns.ACTION: 'bar',
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.TYPE: Param.TYPE_STRING,
            ns.VALUE: 'bar',
        }],
    }]

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.rollback('')


def test_action_transactions_complete(state):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    state.context['command'] = CommandPayload()
    params = [Param('foo', 'bar')]

    action = Action(Service(), state)
    path = [ns.TRANSACTIONS, TransportPayload.TRANSACTION_COMPLETE]
    assert not action._transport.exists(path)
    assert isinstance(action.complete('bar', params), Action)
    assert action._transport.get(path) == [{
        ns.NAME: action.get_name(),
        ns.VERSION: action.get_version(),
        ns.CALLER: action.get_action_name(),
        ns.ACTION: 'bar',
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.TYPE: Param.TYPE_STRING,
            ns.VALUE: 'bar',
        }],
    }]

    # No parameter must be empty
    with pytest.raises(ValueError):
        action.complete('')


def test_action_calls_runtime(mocker, state, schemas, action_reply):
    from kusanagi.sdk import Action
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
    client.call.return_value = (42, transport)
    mocker.patch('kusanagi.sdk.action.Client', return_value=client)

    state.context['schemas'] = schemas
    state.context['command'] = CommandPayload()
    state.context['reply'] = action_reply
    params = [Param('foo')]
    files = [File('foo')]
    files[0].is_local = mocker.Mock(return_value=True)

    action = Action(Service(), state)

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
    assert action.call('baz', '1.0.0', 'blah', params, files, 1000) == 42
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
        action.call('baz', '1.0.0', 'blah', files=files)

    # The remote action must define a return value
    action_schema.has_return.return_value = False
    with pytest.raises(KusanagiError):
        action.call('baz', '1.0.0', 'blah')

    # Call must fail when the call is not defined in the config
    action_schema.has_call.return_value = False
    with pytest.raises(KusanagiError):
        action.call('baz', '1.0.0', 'blah')

    # Call must fail when the schemas are not defined
    action.get_service_schema = mocker.Mock(side_effect=LookupError)
    with pytest.raises(KusanagiError):
        action.call('baz', '1.0.0', 'blah')


def test_action_calls_deferred(mocker, state, schemas, action_reply):
    from kusanagi.sdk import Action
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    state.context['schemas'] = schemas
    state.context['command'] = CommandPayload()
    state.context['reply'] = action_reply
    params = [Param('foo')]
    files = [File('foo')]
    files[0].is_local = mocker.Mock(return_value=True)

    action = Action(Service(), state)

    # Mock the schemas
    schema = mocker.Mock()
    action.get_service_schema = mocker.Mock(return_value=schema)
    action_schema = mocker.Mock()
    schema.get_action_schema = mocker.Mock(return_value=action_schema)

    schema.has_file_server.return_value = True
    action_schema.has_defer_call.return_value = True

    assert not action._transport.exists([ns.CALLS, action.get_name(), action.get_version()])
    assert isinstance(action.defer_call('baz', '1.0.0', 'blah', params, files), Action)
    assert action._transport.get([ns.CALLS, action.get_name(), action.get_version()]) == [{
        ns.NAME: 'baz',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
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
        action.defer_call('baz', '1.0.0', 'blah', files=files)

    # Call must fail when the call is not defined in the config
    action_schema.has_defer_call.return_value = False
    with pytest.raises(KusanagiError):
        action.defer_call('baz', '1.0.0', 'blah')

    # Call must fail when the schemas are not defined
    action.get_service_schema = mocker.Mock(side_effect=LookupError)
    with pytest.raises(KusanagiError):
        action.defer_call('baz', '1.0.0', 'blah')


def test_action_calls_remote(mocker, state, schemas, action_reply):
    from kusanagi.sdk import Action
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError
    from kusanagi.sdk import Param
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    state.context['schemas'] = schemas
    state.context['command'] = CommandPayload()
    state.context['reply'] = action_reply
    params = [Param('foo')]
    files = [File('foo')]
    files[0].is_local = mocker.Mock(return_value=True)

    action = Action(Service(), state)

    # Mock the schemas
    schema = mocker.Mock()
    action.get_service_schema = mocker.Mock(return_value=schema)
    action_schema = mocker.Mock()
    schema.get_action_schema = mocker.Mock(return_value=action_schema)

    schema.has_file_server.return_value = True
    action_schema.has_remote_call.return_value = True

    assert not action._transport.exists([ns.CALLS, action.get_name(), action.get_version()])
    assert isinstance(action.remote_call('ktp://6.6.6.6:77', 'baz', '1.0.0', 'blah', params, files, 1000), Action)
    assert action._transport.get([ns.CALLS, action.get_name(), action.get_version()]) == [{
        ns.GATEWAY: 'ktp://6.6.6.6:77',
        ns.NAME: 'baz',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.TIMEOUT: 1000,
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

    # Remote calls must use the KTP protocol (ktp://)
    with pytest.raises(ValueError):
        action.remote_call('http://6.6.6.6:77', 'baz', '1.0.0', 'blah')

    # Remote calls must fail when there is no file server and a local file is used
    schema.has_file_server.return_value = False
    with pytest.raises(KusanagiError):
        action.remote_call('ktp://6.6.6.6:77', 'baz', '1.0.0', 'blah', files=files)

    # Call must fail when the call is not defined in the config
    action_schema.has_remote_call.return_value = False
    with pytest.raises(KusanagiError):
        action.remote_call('ktp://6.6.6.6:77', 'baz', '1.0.0', 'blah')

    # Call must fail when the schemas are not defined
    action.get_service_schema = mocker.Mock(side_effect=LookupError)
    with pytest.raises(KusanagiError):
        action.remote_call('ktp://6.6.6.6:77', 'baz', '1.0.0', 'blah')


def test_action_errors(state, action_command):
    from kusanagi.sdk import Action
    from kusanagi.sdk import Service
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command

    action = Action(Service(), state)
    address = action._transport.get_public_gateway_address()
    path = [ns.ERRORS, address, action.get_name(), action.get_version()]
    assert not action._transport.exists(path)
    assert isinstance(action.error('Message', 77, 'Status'), Action)
    assert action._transport.get(path) == [{
        ns.MESSAGE: 'Message',
        ns.CODE: 77,
        ns.STATUS: 'Status'
    }]


def test_action_schema_defaults():
    from kusanagi.sdk import ActionSchema
    from kusanagi.sdk import HttpActionSchema
    from kusanagi.sdk.lib.payload.action import ActionSchemaPayload

    schema = ActionSchema('foo', ActionSchemaPayload())
    assert schema.get_timeout() == ActionSchema.DEFAULT_EXECUTION_TIMEOUT
    assert not schema.is_deprecated()
    assert not schema.is_collection()
    assert schema.get_name() == 'foo'
    assert schema.get_entity_path() == ''
    assert schema.get_path_delimiter() == '/'
    assert not schema.has_entity()
    assert schema.get_entity() == {}
    assert not schema.has_relations()
    assert schema.get_relations() == []
    assert schema.get_calls() == []
    assert not schema.has_call('foo', '1.0.0', 'bar')
    assert not schema.has_calls()
    assert schema.get_defer_calls() == []
    assert not schema.has_defer_call('foo', '1.0.0', 'bar')
    assert not schema.has_defer_calls()
    assert schema.get_remote_calls() == []
    assert not schema.has_remote_call('ktp://6.6.6.6:77', 'foo', '1.0.0', 'bar')
    assert not schema.has_remote_calls()
    assert not schema.has_return()

    with pytest.raises(ValueError):
        schema.get_return_type()

    assert schema.get_params() == []
    assert not schema.has_param('foo')

    with pytest.raises(LookupError):
        schema.get_param_schema('foo')

    assert schema.get_files() == []
    assert not schema.has_file('bar')

    with pytest.raises(LookupError):
        schema.get_file_schema('bar')

    assert schema.get_tags() == []
    assert not schema.has_tag('foo')

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpActionSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_method() == HttpActionSchema.DEFAULT_METHOD
    assert http_schema.get_path() == ''
    assert http_schema.get_input() == HttpActionSchema.DEFAULT_INPUT
    assert http_schema.get_body() == HttpActionSchema.DEFAULT_BODY


def test_action_schema():
    from kusanagi.sdk import ActionSchema
    from kusanagi.sdk import FileSchema
    from kusanagi.sdk import HttpActionSchema
    from kusanagi.sdk import ParamSchema
    from kusanagi.sdk.lib import datatypes
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.action import ActionSchemaPayload

    payload = ActionSchemaPayload({
        ns.TIMEOUT: 1234,
        ns.DEPRECATED: True,
        ns.COLLECTION: True,
        ns.ENTITY_PATH: 'a|b|c',
        ns.PATH_DELIMITER: '|',
        ns.ENTITY: {
            ns.FIELD: [{
                ns.NAME: 'foo',
            }],
        },
        ns.RELATIONS: [{
            ns.NAME: 'first',
        }],
        ns.CALLS: [['foo', '1.0.0', 'bar']],
        ns.DEFERRED_CALLS: [['foo', '1.0.0', 'bar']],
        ns.REMOTE_CALLS: [['ktp://6.6.6.6:77', 'foo', '1.0.0', 'bar']],
        ns.RETURN: {
            ns.TYPE: datatypes.TYPE_INTEGER,
        },
        ns.PARAMS: {
            'foo': {
                ns.NAME: 'foo',
            }
        },
        ns.FILES: {
            'bar': {
                ns.NAME: 'bar',
            }
        },
        ns.TAGS: ['foo'],
        ns.HTTP: {
            ns.GATEWAY: False,
            ns.METHOD: 'PUT',
            ns.PATH: '/test',
            ns.INPUT: 'path',
            ns.BODY: ['custom/type'],
        },
    })

    schema = ActionSchema('foo', payload)
    assert schema.get_timeout() == payload.get([ns.TIMEOUT])
    assert schema.is_deprecated()
    assert schema.is_collection()
    assert schema.get_name() == 'foo'
    assert schema.get_entity_path() == payload.get([ns.ENTITY_PATH])
    assert schema.get_path_delimiter() == payload.get([ns.PATH_DELIMITER])
    assert schema.resolve_entity({'a': {'b': {'c': {'name': 'foo'}}}}) == {'name': 'foo'}
    # Check that an exception is raised when the entity is not resolved
    with pytest.raises(LookupError):
        schema.resolve_entity({'a': {'b': 42}})

    assert schema.has_entity()
    assert schema.get_entity() == {
        'field': [{'name': 'foo', 'optional': False, 'type': 'string'}],
        'validate': False,
    }
    assert schema.has_relations()
    assert schema.get_relations() == [['one', 'first']]
    assert schema.get_calls() == payload.get([ns.CALLS])
    assert schema.has_call('foo', '1.0.0', 'bar')
    assert not schema.has_call('foo', '1.0.0', 'invalid')
    assert not schema.has_call('foo', 'invalid', 'invalid')
    assert not schema.has_call('invalid', 'invalid', 'invalid')
    assert schema.has_calls()
    assert schema.get_defer_calls() == payload.get([ns.DEFERRED_CALLS])
    assert schema.has_defer_call('foo', '1.0.0', 'bar')
    assert not schema.has_defer_call('foo', '1.0.0', 'invalid')
    assert not schema.has_defer_call('foo', 'invalid', 'invalid')
    assert not schema.has_defer_call('invalid', 'invalid', 'invalid')
    assert schema.has_defer_calls()
    assert schema.get_remote_calls() == payload.get([ns.REMOTE_CALLS])
    assert schema.has_remote_call('ktp://6.6.6.6:77', 'foo', '1.0.0', 'bar')
    assert not schema.has_remote_call('ktp://6.6.6.6:77', 'foo', '1.0.0', 'invalid')
    assert not schema.has_remote_call('ktp://6.6.6.6:77', 'foo', 'invalid', 'invalid')
    assert not schema.has_remote_call('ktp://6.6.6.6:77', 'invalid', 'invalid', 'invalid')
    assert not schema.has_remote_call('invalid', 'invalid', 'invalid', 'invalid')
    assert schema.has_remote_calls()
    assert schema.has_return()
    assert schema.get_return_type() == datatypes.TYPE_INTEGER

    assert schema.get_params() == ['foo']
    assert schema.has_param('foo')
    param_schema = schema.get_param_schema('foo')
    assert isinstance(param_schema, ParamSchema)
    assert param_schema.get_name() == 'foo'

    assert schema.get_files() == ['bar']
    assert schema.has_file('bar')
    file_schema = schema.get_file_schema('bar')
    assert isinstance(file_schema, FileSchema)
    assert file_schema.get_name() == 'bar'

    assert schema.get_tags() == ['foo']
    assert schema.has_tag('foo')

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpActionSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_method() == payload.get([ns.HTTP, ns.METHOD])
    assert http_schema.get_path() == payload.get([ns.HTTP, ns.PATH])
    assert http_schema.get_input() == payload.get([ns.HTTP, ns.INPUT])
    assert http_schema.get_body() == payload.get([ns.HTTP, ns.BODY])[0]
