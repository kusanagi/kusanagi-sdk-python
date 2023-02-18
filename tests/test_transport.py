# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_transport_defaults():
    from kusanagi.sdk import File
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    transport = Transport(TransportPayload())
    assert transport.get_request_id() == ''
    assert transport.get_request_timestamp() == ''
    assert transport.get_origin_service() == tuple()
    assert transport.get_origin_duration() == 0
    assert transport.get_property('foo') == ''
    assert transport.get_property('foo', default='ok') == 'ok'
    assert transport.get_properties() == {}
    assert not transport.has_download()
    assert isinstance(transport.get_download(), File)
    assert list(transport.get_data()) == []
    assert list(transport.get_relations()) == []
    assert list(transport.get_links()) == []
    assert list(transport.get_calls()) == []
    assert list(transport.get_errors()) == []
    assert transport.get_transactions('commit') == []

    # Default value for a property must be sring
    with pytest.raises(TypeError):
        transport.get_property('foo', default=42)

    # Invalid transactions must fail
    with pytest.raises(ValueError):
        assert transport.get_transactions('invalid')


def test_transport():
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.META: {
            ns.ID: '25759c6c-8531-40d2-a415-4ff9246307c5',
            ns.DATETIME: '2017-01-27T20:12:08.952811+00:00',
            ns.ORIGIN: ['foo', '1.0.0', 'bar'],
            ns.DURATION: 18,
            ns.PROPERTIES: {'foo': 'bar'},
        },
        ns.BODY: {
            ns.NAME: 'blah',
        },
    })
    transport = Transport(payload)
    assert transport.get_request_id() == payload.get([ns.META, ns.ID])
    assert transport.get_request_timestamp() == payload.get([ns.META, ns.DATETIME])
    assert transport.get_origin_service() == tuple(payload.get([ns.META, ns.ORIGIN]))
    assert transport.get_origin_duration() == payload.get([ns.META, ns.DURATION])
    assert transport.get_property('foo') == 'bar'
    assert transport.get_property('foo', default='ok') == 'bar'
    assert transport.get_properties() == payload.get([ns.META, ns.PROPERTIES])
    assert transport.has_download()
    file = transport.get_download()
    assert file is not None
    assert file.get_name() == payload.get([ns.BODY, ns.NAME])


def test_transport_data():
    from kusanagi.sdk import ServiceData
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.DATA: {
            'http://1.2.3.4:77': {
                'foo': {
                    '1.2.3': {
                        'bar': [{'value': 'first'}]
                    },
                },
                'baz': {
                    '2.3.4': {
                        'blah': [{'value': 'second'}]
                    },
                },
            },
            'ktp://1.2.3.4:77': {
                'kfoo': {
                    '1.2.3': {
                        'kbar': [{'value': 'third'}]
                    },
                },
            },
        },
    })
    transport = Transport(payload)
    items = list(transport.get_data())
    assert len(items) == 3
    for data in items:
        assert isinstance(data, ServiceData)
        path = [ns.DATA, data.get_address(), data.get_name(), data.get_version()]
        assert payload.exists(path)
        actions_payload = payload.get(path)
        for action_data in data.get_actions():
            assert actions_payload.get(action_data.get_name()) == action_data.get_data()


def test_transport_relations():
    from kusanagi.sdk import ForeignRelation
    from kusanagi.sdk import Relation
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.RELATIONS: {
            'http://1.2.3.4:77': {
                'foo': {
                    '11': {
                        'http://1.2.3.4:77': {
                            'bar': '1'
                        },
                    },
                },
                'baz': {
                    '3': {
                        'ktp://1.2.3.4:77': {
                            'kfoo': ['12', '44']
                        },
                    },
                },
            },
            'ktp://1.2.3.4:77': {
                'kfoo': {
                    '44': {
                        'http://1.2.3.4:77': {
                            'foo': ['77']
                        },
                    },
                },
            },
        },
    })
    transport = Transport(payload)
    relations = list(transport.get_relations())
    assert len(relations) == 3
    for relation in relations:
        assert isinstance(relation, Relation)
        path = [ns.RELATIONS, relation.get_address(), relation.get_name(), relation.get_primary_key()]
        assert payload.exists(path)
        for foreign in relation.get_foreign_relations():
            assert isinstance(foreign, ForeignRelation)
            path.extend([foreign.get_address(), foreign.get_name()])
            assert payload.exists(path)
            keys = payload.get(path)
            if not isinstance(keys, list):
                keys = [keys]

            assert keys == foreign.get_foreign_keys()


def test_transport_links():
    from kusanagi.sdk import Link
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.LINKS: {
            'http://1.2.3.4:77': {
                'foo': {
                    'first': 'http://test.com/first',
                },
                'baz': {
                    'second': 'http://test.com/second',
                },
            },
            'ktp://1.2.3.4:77': {
                'kfoo': {
                    'third': 'http://test.com/third',
                },
            },
        },
    })
    transport = Transport(payload)
    links = list(transport.get_links())
    assert len(links) == 3
    for link in links:
        assert isinstance(link, Link)
        assert payload.get([ns.LINKS, link.get_address(), link.get_name(), link.get_link()]) == link.get_uri()


def test_transport_calls():
    from kusanagi.sdk import Callee
    from kusanagi.sdk import Caller
    from kusanagi.sdk import Param
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.CALLS: {
            'foo': {
                '1.2.3': [{
                    ns.CALLER: 'bar',
                    ns.DURATION: 18,
                    ns.TIMEOUT: 10001,
                    ns.NAME: 'baz',
                    ns.VERSION: '1.2.3',
                    ns.ACTION: 'blah',
                    ns.PARAMS: [{
                        ns.NAME: 'message',
                        ns.VALUE: 'hola',
                        ns.TYPE: 'string',
                    }],
                }],
            },
            'baz': {
                '1.2.3': [{
                    ns.CALLER: 'blah',
                    ns.GATEWAY: 'ktp://1.2.3.4:77',
                    ns.NAME: 'other',
                    ns.VERSION: '1.6.3',
                    ns.ACTION: 'test',
                    ns.TIMEOUT: 10002,
                    ns.PARAMS: [{
                        ns.NAME: 'age',
                        ns.VALUE: 42,
                        ns.TYPE: 'integer',
                    }],
                }],
            },
        },
    })
    transport = Transport(payload)
    calls = list(transport.get_calls())
    assert len(calls) == 2
    for caller in calls:
        assert isinstance(caller, Caller)
        path = [ns.CALLS, caller.get_name(), caller.get_version()]
        assert payload.exists(path)
        call_data = payload.get(path)[0]
        assert caller.get_action() == call_data.get(ns.CALLER)

        callee = caller.get_callee()
        assert isinstance(callee, Callee)
        assert callee.get_address() == call_data.get(ns.GATEWAY, '')
        assert callee.get_timeout() == call_data.get(ns.TIMEOUT)
        assert callee.get_name() == call_data.get(ns.NAME)
        assert callee.get_version() == call_data.get(ns.VERSION)
        assert callee.get_action() == call_data.get(ns.ACTION)

        params = callee.get_params()
        assert len(params) == 1
        param = params[0]
        assert isinstance(param, Param)
        param_data = call_data[ns.PARAMS][0]
        assert param.get_name() == param_data[ns.NAME]
        assert param.get_type() == param_data[ns.TYPE]
        assert param.get_value() == param_data[ns.VALUE]


def test_transport_transactions():
    from kusanagi.sdk import Param
    from kusanagi.sdk import Transaction
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    # Mapping between user types and payload short names
    types = {
        Transaction.TYPE_COMMIT: TransportPayload.TRANSACTION_COMMIT,
        Transaction.TYPE_ROLLBACK: TransportPayload.TRANSACTION_ROLLBACK,
    }

    payload = TransportPayload({
        ns.TRANSACTIONS: {
            ns.COMMIT: [{
                ns.NAME: 'foo',
                ns.VERSION: '1.2.3',
                ns.ACTION: 'bar',
                ns.CALLER: 'baz',
                ns.PARAMS: [{
                    ns.NAME: 'message',
                    ns.VALUE: 'hola',
                    ns.TYPE: 'string',
                }],
            }],
            ns.ROLLBACK: [{
                ns.NAME: 'first',
                ns.VERSION: '1.3.5',
                ns.ACTION: 'blah',
                ns.CALLER: 'second',
                ns.PARAMS: [{
                    ns.NAME: 'age',
                    ns.VALUE: 42,
                    ns.TYPE: 'integer',
                }],
            }],
        },
    })
    transport = Transport(payload)
    for transaction_type in types.keys():
        transactions = transport.get_transactions(transaction_type)
        assert len(transactions) == 1
        transaction = transactions[0]
        assert isinstance(transaction, Transaction)
        path = [ns.TRANSACTIONS, types[transaction.get_type()]]
        assert payload.exists(path)
        tr_data = payload.get(path)[0]
        assert transaction.get_name() == tr_data[ns.NAME]
        assert transaction.get_version() == tr_data[ns.VERSION]
        assert transaction.get_callee_action() == tr_data[ns.ACTION]
        assert transaction.get_caller_action() == tr_data[ns.CALLER]

        params = transaction.get_params()
        assert len(params) == 1
        param = params[0]
        assert isinstance(param, Param)
        param_data = tr_data[ns.PARAMS][0]
        assert param.get_name() == param_data[ns.NAME]
        assert param.get_type() == param_data[ns.TYPE]
        assert param.get_value() == param_data[ns.VALUE]


def test_transport_errors():
    from kusanagi.sdk import Error
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    payload = TransportPayload({
        ns.ERRORS: {
            'http://1.2.3.4:77': {
                'foo': {
                    '1.2.3': [{
                        ns.MESSAGE: 'First',
                        ns.CODE: 1,
                        ns.STATUS: '100',
                    }],
                },
            },
            'ktp://1.2.3.4:77': {
                'kfoo': {
                    '1.2.3': [{
                        ns.MESSAGE: 'Second',
                        ns.CODE: 2,
                        ns.STATUS: '200',
                    }],
                },
            },
        },
    })
    transport = Transport(payload)
    errors = list(transport.get_errors())
    assert len(errors) == 2
    for error in errors:
        assert isinstance(error, Error)
        path = [ns.ERRORS, error.get_address(), error.get_name(), error.get_version()]
        assert payload.exists(path)
        error_data = payload.get(path)[0]
        assert error.get_message() == error_data[ns.MESSAGE]
        assert error.get_code() == error_data[ns.CODE]
        assert error.get_status() == error_data[ns.STATUS]
