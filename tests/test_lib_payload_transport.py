# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_lib_payload_transport_defaults():
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload()
    assert payload.get_public_gateway_address() == ''
    assert not payload.has_calls('foo', '1.2.3')
    assert not payload.has_files()
    assert not payload.has_transactions()
    assert not payload.has_download()
    assert not payload.set_return(42)


def test_lib_payload_transport():
    from kusanagi.sdk import File
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    reply = ReplyPayload()

    payload = TransportPayload({
        ns.META: {
            ns.GATEWAY: ['', 'http://1.2.3.4:77'],
        },
        ns.CALLS: {
            'foo': {
                '1.2.3': [{}],
            },
        },
        ns.FILES: {},
        ns.TRANSACTIONS: {},
        ns.BODY: {},
    })
    assert isinstance(payload.set_reply(reply), TransportPayload)
    assert payload.get_public_gateway_address() == payload.get([ns.META, ns.GATEWAY])[1]
    assert payload.has_calls('foo', '1.2.3')
    assert payload.has_files()
    assert payload.has_transactions()
    assert payload.set_download(File('foo'))
    assert payload.has_download()
    assert payload.get([ns.BODY, ns.NAME]) == 'foo'
    assert payload.set_return(42)
    assert reply.get([ns.RETURN]) == 42

    # The "set" method must update the transport payload and the reply
    assert reply.get([ns.TRANSPORT, 'foo']) is None
    assert payload.get(['foo']) is None
    assert payload.set(['foo'], 42)
    assert payload.get(['foo']) == 42
    assert reply.get([ns.TRANSPORT, 'foo']) == 42

    # The "append" method must update the transport payload and the reply
    assert reply.get([ns.TRANSPORT, 'bar']) is None
    assert payload.get(['bar']) is None
    assert payload.append(['bar'], 42)
    assert payload.get(['bar']) == [42]
    assert reply.get([ns.TRANSPORT, 'bar']) == [42]

    # The "extend" method must update the transport payload and the reply
    assert payload.extend(['bar'], [77])
    assert payload.get(['bar']) == [42, 77]
    assert reply.get([ns.TRANSPORT, 'bar']) == [42, 77]

    # The "delete" method must update the transport payload and the reply
    assert payload.delete(['bar'])
    assert payload.get(['bar']) is None
    assert reply.get([ns.TRANSPORT, 'bar']) is None


def test_lib_payload_transport_merge_runtime_transport():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    # Create a reply and a transport payload where a new payload must be merged
    reply = ReplyPayload()
    payload = TransportPayload({
        ns.META: {
            ns.ID: '25759c6c-8531-40d2-a415-4ff9246307c5',
        },
        ns.DATA: {'a': {'b': [2]}},
    })
    payload.set_reply(reply)
    # Merge the data from a new payload
    assert payload.merge_runtime_call_transport(TransportPayload({
        ns.META: {
            ns.ID: '25759c6c-8531-40d2-a415-4ff9246307c5',
        },
        ns.DATA: {'a': {'b': [3], 'c': 4}},
    }))
    # Both, the transport and the reply must contain their original data and the new data
    assert payload == reply.get([ns.TRANSPORT]) == {
        ns.META: {
            ns.ID: '25759c6c-8531-40d2-a415-4ff9246307c5',
        },
        ns.DATA: {'a': {'b': [2, 3], 'c': 4}},
    }

    # The transport to merge must be a transport payload
    with pytest.raises(TypeError):
        payload.merge_runtime_call_transport({})


def test_lib_payload_transport_data():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    address = 'http://1.2.3.4:77'
    payload = TransportPayload({
        ns.META: {
            ns.GATEWAY: ['', address],
        },
    })
    assert payload.add_data('foo', '1.2.3', 'bar', {})
    assert payload.get([ns.DATA, address, 'foo', '1.2.3', 'bar']) == [{}]


def test_lib_payload_transport_relations():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    address = 'http://1.2.3.4:77'
    remote = 'http://6.6.6.6:77'
    payload = TransportPayload({
        ns.META: {
            ns.GATEWAY: ['', address],
        },
    })
    assert payload.add_relate_one('foo', '1', 'bar', '2')
    assert payload.get([ns.RELATIONS, address, 'foo', '1', address, 'bar']) == '2'
    assert payload.add_relate_many('foo', '1', 'bar', ['2', '3'])
    assert payload.get([ns.RELATIONS, address, 'foo', '1', address, 'bar']) == ['2', '3']
    assert payload.add_relate_one_remote('foo', '1', remote, 'bar', '4')
    assert payload.get([ns.RELATIONS, address, 'foo', '1', remote, 'bar']) == '4'
    assert payload.add_relate_many_remote('foo', '1', remote, 'bar', ['4', '5'])
    assert payload.get([ns.RELATIONS, address, 'foo', '1', remote, 'bar']) == ['4', '5']


def test_lib_payload_transport_link():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    address = 'http://1.2.3.4:77'
    payload = TransportPayload({
        ns.META: {
            ns.GATEWAY: ['', address],
        },
    })
    assert payload.add_link('foo', 'self', '/test')
    assert payload.get([ns.LINKS, address, 'foo', 'self']) == '/test'


def test_lib_payload_transport_calls_runtime():
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    params = [Param('foo')]
    files = [File('bar')]

    payload = TransportPayload()
    assert not payload.has_calls('foo', '1.2.3')
    assert payload.add_call('foo', '1.2.3', 'bar', 'baz', '3.2.1', 'blah', 42, params, files, 1000)
    assert payload.get([ns.CALLS, 'foo', '1.2.3']) == [{
        ns.NAME: 'baz',
        ns.VERSION: '3.2.1',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.DURATION: 42,
        ns.TIMEOUT: 1000,
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: '',
            ns.TYPE: Param.TYPE_STRING,
        }],
        ns.FILES: [{
            ns.NAME: 'bar',
            ns.PATH: '',
            ns.MIME: '',
            ns.FILENAME: '',
            ns.SIZE: 0,
        }],
    }]
    # Runtime calls are no accounted as calls during userland actions
    assert not payload.has_calls('foo', '1.2.3')

    # Runtime calls must require a valid duration
    with pytest.raises(ValueError):
        payload.add_call('foo', '1.2.3', 'bar', 'baz', '3.2.1', 'blah', None)


def test_lib_payload_transport_calls_runtime_with_transport():
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    params = [Param('foo')]
    files = [File('bar')]

    transport = TransportPayload()
    payload = TransportPayload()
    assert payload.add_call('foo', '1.2.3', 'bar', 'baz', '3.2.1', 'blah', 42, params, files, 1000, transport)
    # Call info must also be added to the transport argument value
    assert transport.get([ns.CALLS, 'foo', '1.2.3']) == [{
        ns.NAME: 'baz',
        ns.VERSION: '3.2.1',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.DURATION: 42,
        ns.TIMEOUT: 1000,
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: '',
            ns.TYPE: Param.TYPE_STRING,
        }],
        ns.FILES: [{
            ns.NAME: 'bar',
            ns.PATH: '',
            ns.MIME: '',
            ns.FILENAME: '',
            ns.SIZE: 0,
        }],
    }]


def test_lib_payload_transport_calls_deferred():
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    params = [Param('foo')]
    files = [File('bar')]
    payload = TransportPayload()
    assert not payload.has_calls('foo', '1.2.3')

    assert payload.add_defer_call('foo', '1.2.3', 'bar', 'baz', '3.2.1', 'blah', params, files)
    assert payload.get([ns.CALLS, 'foo', '1.2.3']) == [{
        ns.NAME: 'baz',
        ns.VERSION: '3.2.1',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: '',
            ns.TYPE: Param.TYPE_STRING,
        }],
        ns.FILES: [{
            ns.NAME: 'bar',
            ns.PATH: '',
            ns.MIME: '',
            ns.FILENAME: '',
            ns.SIZE: 0,
        }],
    }]
    assert payload.has_calls('foo', '1.2.3')


def test_lib_payload_transport_calls_remote():
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    address = 'http://1.2.3.4:77'
    params = [Param('foo')]
    files = [File('bar')]
    payload = TransportPayload()
    assert not payload.has_calls('foo', '1.2.3')

    assert payload.add_remote_call(address, 'foo', '1.2.3', 'bar', 'baz', '3.2.1', 'blah', params, files, 1000)
    assert payload.get([ns.CALLS, 'foo', '1.2.3']) == [{
        ns.GATEWAY: address,
        ns.NAME: 'baz',
        ns.VERSION: '3.2.1',
        ns.ACTION: 'blah',
        ns.CALLER: 'bar',
        ns.TIMEOUT: 1000,
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: '',
            ns.TYPE: Param.TYPE_STRING,
        }],
        ns.FILES: [{
            ns.NAME: 'bar',
            ns.PATH: '',
            ns.MIME: '',
            ns.FILENAME: '',
            ns.SIZE: 0,
        }],
    }]
    assert payload.has_calls('foo', '1.2.3')


def test_lib_payload_transport_transactions():
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    transaction_type = TransportPayload.TRANSACTION_COMMIT
    payload = TransportPayload()
    assert not payload.has_transactions()
    assert payload.add_transaction(transaction_type, 'foo', '1.2.3', 'bar', 'baz', [Param('blah')])
    assert payload.get([ns.TRANSACTIONS, transaction_type]) == [{
        ns.NAME: 'foo',
        ns.VERSION: '1.2.3',
        ns.CALLER: 'bar',
        ns.ACTION: 'baz',
        ns.PARAMS: [{
            ns.NAME: 'blah',
            ns.TYPE: Param.TYPE_STRING,
            ns.VALUE: '',
        }],
    }]
    assert payload.has_transactions()
    assert len(payload.get([ns.TRANSACTIONS])) == 1

    transaction_type = TransportPayload.TRANSACTION_ROLLBACK
    assert payload.add_transaction(transaction_type, 'other', '1.2.3', 'bar', 'baz')
    assert payload.get([ns.TRANSACTIONS, transaction_type]) == [{
        ns.NAME: 'other',
        ns.VERSION: '1.2.3',
        ns.CALLER: 'bar',
        ns.ACTION: 'baz',
    }]
    assert len(payload.get([ns.TRANSACTIONS])) == 2

    with pytest.raises(ValueError):
        payload.add_transaction('invalid', 'foo', '1.2.3', 'bar', 'baz')


def test_lib_payload_transport_error():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    address = 'http://1.2.3.4:77'
    payload = TransportPayload({
        ns.META: {
            ns.GATEWAY: ['', address],
        },
    })
    assert payload.add_error('foo', '1.2.3', 'Message', 42, 'Error')
    assert payload.add_error('foo', '1.2.3', 'Other', 77, 'Exception')
    assert payload.get([ns.ERRORS, address, 'foo', '1.2.3']) == [{
        ns.MESSAGE: 'Message',
        ns.CODE: 42,
        ns.STATUS: 'Error',
    }, {
        ns.MESSAGE: 'Other',
        ns.CODE: 77,
        ns.STATUS: 'Exception',
    }]
    assert payload.add_error('other', '2.2.3', 'Other', 77, 'Exception')
    assert payload.get([ns.ERRORS, address, 'other', '2.2.3']) == [{
        ns.MESSAGE: 'Other',
        ns.CODE: 77,
        ns.STATUS: 'Exception',
    }]
