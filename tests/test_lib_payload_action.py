# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_lib_payload_action_schema_defaults():
    from kusanagi.sdk.lib.payload.action import ActionSchemaPayload
    from kusanagi.sdk.lib.payload.action import HttpActionSchemaPayload

    schema = ActionSchemaPayload()
    assert schema.get_entity() == {}
    assert schema.get_relations() == []
    assert schema.get_param_names() == []
    assert schema.get_file_names() == []
    assert isinstance(schema.get_http_action_schema_payload(), HttpActionSchemaPayload)

    with pytest.raises(KeyError):
        schema.get_param_schema_payload('foo')

    with pytest.raises(KeyError):
        schema.get_file_schema_payload('foo')


def test_lib_payload_action_schema():
    from kusanagi.sdk.lib import datatypes
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.action import ActionSchemaPayload
    from kusanagi.sdk.lib.payload.file import FileSchemaPayload
    from kusanagi.sdk.lib.payload.action import HttpActionSchemaPayload
    from kusanagi.sdk.lib.payload.param import ParamSchemaPayload

    payload = {
        ns.ENTITY: {
            ns.FIELDS: [{
                ns.NAME: "contact",
                ns.FIELD: [{
                    ns.NAME: "id",
                    ns.TYPE: datatypes.TYPE_INTEGER,
                }, {
                    ns.NAME: "email",
                }],
                ns.OPTIONAL: False,
            }],
            ns.FIELD: [{
                ns.NAME: "id",
                ns.TYPE: datatypes.TYPE_INTEGER,
            }, {
                ns.NAME: "name",
                ns.TYPE: datatypes.TYPE_STRING,
            }, {
                ns.NAME: "is_admin",
                ns.TYPE: datatypes.TYPE_BOOLEAN,
                ns.OPTIONAL: True,
            }],
            ns.VALIDATE: True,
            ns.PRIMARY_KEY: "pk",
        },
        ns.RELATIONS: [{
            ns.TYPE: 'many',
            ns.NAME: 'foo',
        }, {
            ns.NAME: 'bar',
        }],
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
        ns.HTTP: {
            ns.ENTITY_PATH: '/entity',
        },
    }

    schema = ActionSchemaPayload(payload)
    assert schema.get_entity() == {
        'field': [
            {'name': 'id', 'optional': False, 'type': 'integer'},
            {'name': 'name', 'optional': False, 'type': 'string'},
            {'name': 'is_admin', 'optional': True, 'type': 'boolean'},
        ],
        'fields': [{
            'field': [
                {'name': 'id', 'optional': False, 'type': 'integer'},
                {'name': 'email', 'optional': False, 'type': 'string'},
            ],
            'name': 'contact',
            'optional': False,
        }],
        'validate': True,
    }
    assert schema.get_relations() == [
        ['many', 'foo'],
        ['one', 'bar'],
    ]
    assert schema.get_param_names() == ['foo']
    param_schema = schema.get_param_schema_payload('foo')
    assert isinstance(param_schema, ParamSchemaPayload)
    assert param_schema.get(ns.NAME) == 'foo'
    assert schema.get_file_names() == ['bar']
    file_schema = schema.get_file_schema_payload('bar')
    assert isinstance(file_schema, FileSchemaPayload)
    assert file_schema.get(ns.NAME) == 'bar'
    assert isinstance(schema.get_http_action_schema_payload(), HttpActionSchemaPayload)
