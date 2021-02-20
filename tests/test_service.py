# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_service():
    from kusanagi.sdk import Service

    def callback(request):
        pass

    service = Service()
    assert 'foo' not in service._callbacks
    assert service.action('foo', callback) == service
    assert service._callbacks.get('foo') == callback


def test_service_schema_defaults():
    from kusanagi.sdk import HttpServiceSchema
    from kusanagi.sdk import ServiceSchema
    from kusanagi.sdk.lib.payload.service import ServiceSchemaPayload

    schema = ServiceSchema(ServiceSchemaPayload({}, name='foo', version='1.0.0'))
    assert schema.get_name() == 'foo'
    assert schema.get_version() == '1.0.0'
    assert schema.get_address() == ''
    assert not schema.has_file_server()
    assert schema.get_actions() == []
    assert not schema.has_action('foo')
    assert isinstance(schema.get_http_schema(), HttpServiceSchema)

    with pytest.raises(LookupError):
        schema.get_action_schema('foo')


def test_service_schema(service_schema):
    from kusanagi.sdk import ActionSchema
    from kusanagi.sdk import ServiceSchema
    from kusanagi.sdk.lib.payload import ns

    schema = ServiceSchema(service_schema)
    assert schema.get_name() == service_schema.get_name()
    assert schema.get_version() == service_schema.get_version()
    assert schema.get_address() == service_schema.get([ns.ADDRESS])
    assert schema.has_file_server()
    assert schema.get_actions() == ['foo']
    assert schema.has_action('foo')
    assert isinstance(schema.get_action_schema('foo'), ActionSchema)


def test_service_http_schema_defaults():
    from kusanagi.sdk import ServiceSchema
    from kusanagi.sdk.lib.payload.service import ServiceSchemaPayload

    schema = ServiceSchema(ServiceSchemaPayload({}, name='foo', version='1.0.0'))
    http_schema = schema.get_http_schema()
    assert http_schema.is_accessible()
    assert http_schema.get_base_path() == ''


def test_service_http_schema(service_schema):
    from kusanagi.sdk import ServiceSchema
    from kusanagi.sdk.lib.payload import ns

    schema = ServiceSchema(service_schema)
    http_schema = schema.get_http_schema()
    assert not http_schema.is_accessible()
    assert http_schema.get_base_path() == service_schema.get([ns.HTTP, ns.BASE_PATH])
