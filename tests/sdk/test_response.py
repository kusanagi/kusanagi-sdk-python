import pytest

from kusanagi import urn
from kusanagi.sdk.response import NoReturnValueDefined
from kusanagi.sdk.response import Response
from kusanagi.sdk.transport import Transport
from kusanagi.sdk.http.request import HttpRequest
from kusanagi.sdk.http.response import HttpResponse
from kusanagi.schema import SchemaRegistry


def test_sdk_response():
    SchemaRegistry()

    values = {
        'attributes': {},
        'transport': Transport({'meta': {'origin': ['foo', '1.0.0', 'bar']}}),
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        }

    response = Response(**values)
    assert response.get_gateway_protocol() == values['gateway_protocol']
    assert response.get_gateway_address() == values['gateway_addresses'][1]
    assert response.get_transport() == values['transport']
    # By default no HTTP request or response are created
    assert response.get_http_request() is None
    assert response.get_http_response() is None
    # No return value is defined
    with pytest.raises(NoReturnValueDefined):
        response.get_return()

    # Create a new response with HTTP request and response data
    values['http_request'] = {
        'method': 'GET',
        'url': 'http://foo.com/bar/index/',
        }
    values['http_response'] = {
        'status_code': 200,
        'status_text': 'OK',
        }
    response = Response(**values)
    assert isinstance(response.get_http_request(), HttpRequest)
    assert isinstance(response.get_http_response(), HttpResponse)

    values['return_value'] = 42
    response = Response(**values)
    assert response.get_return() == 42

    # Remove the origin to cover a specific get return case
    del values['return_value']
    values['transport'] = Transport({})
    response = Response(**values)
    assert response.get_return() is None



def test_response_log(mocker, logs):
    SchemaRegistry()

    values = {
        'attributes': {},
        'transport': Transport({'meta': {'id': 'TEST'}}),
        'component': object(),
        'path': '/path/to/file.py',
        'name': 'dummy',
        'version': '1.0',
        'framework_version': '1.0.0',
        'gateway_protocol': urn.HTTP,
        'gateway_addresses': ['12.34.56.78:1234', 'http://127.0.0.1:80'],
        'debug': True,
        }
    response = Response(**values)
    assert response.is_debug()
    log_message = 'Test log message'
    response.log(log_message)
    out = logs.getvalue()
    assert out.rstrip().split(' |')[0].endswith(log_message)
