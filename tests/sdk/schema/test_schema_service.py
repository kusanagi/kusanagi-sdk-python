import pytest

from kusanagi.sdk.schema.action import ActionSchema
from kusanagi.sdk.schema.service import HttpServiceSchema
from kusanagi.sdk.schema.service import ServiceSchema
from kusanagi.sdk.schema.service import ServiceSchemaError
from kusanagi.payload import Payload


def test_sdk_schema_service_defaults():
    service = ServiceSchema('foo', '1.0', {})

    assert service.get_name() == 'foo'
    assert service.get_version() == '1.0'
    assert not service.has_file_server()
    assert service.get_actions() == []
    assert not service.has_action('bar')

    # By default there are no action schemas because payload is empty
    with pytest.raises(ServiceSchemaError):
        service.get_action_schema('bar')

    http_schema = service.get_http_schema()
    assert isinstance(http_schema, HttpServiceSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_base_path() == ''


def test_sdk_schema_service(read_json):
    payload = Payload(read_json('schema-service'))
    service = ServiceSchema('foo', '1.0', payload)

    assert service.get_name() == 'foo'
    assert service.get_version() == '1.0'
    assert service.has_file_server()
    assert sorted(service.get_actions()) == ['defaults', 'foo']
    assert service.has_action('foo')
    assert service.has_action('defaults')

    # Check action schema
    action_schema = service.get_action_schema('foo')
    assert isinstance(action_schema, ActionSchema)

    # Check HTTP schema
    http_schema = service.get_http_schema()
    assert isinstance(http_schema, HttpServiceSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_base_path() == payload.get('http/base_path')
