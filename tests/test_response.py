# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_response_defaults(state):
    from kusanagi.sdk import HttpRequest
    from kusanagi.sdk import HttpResponse
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    command = CommandPayload()
    command.set([ns.TRANSPORT], {
        ns.META: {
            ns.ORIGIN: ['foo', '1.0.0', 'bar'],
        }
    })
    state.context['command'] = command
    state.context['reply'] = ReplyPayload()

    response = Response(Middleware(), state)
    assert response.get_gateway_protocol() == ''
    assert response.get_gateway_address() == ''
    assert response.get_request_attribute('foo') == ''
    assert response.get_request_attributes() == {}
    assert isinstance(response.get_http_response(), HttpResponse)
    assert isinstance(response.get_http_request(), HttpRequest)
    assert not response.has_return()
    assert isinstance(response.get_transport(), Transport)

    # There is no return value
    with pytest.raises(ValueError):
        response.get_return()


def test_response(state, action_command):
    from kusanagi.sdk import HttpRequest
    from kusanagi.sdk import HttpResponse
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk import Transport
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    action_command.set([ns.RETURN], 42)
    state.context['command'] = action_command
    state.context['reply'] = ReplyPayload()

    response = Response(Middleware(), state)
    assert response.get_gateway_protocol() == action_command.get([ns.META, ns.PROTOCOL])
    assert response.get_gateway_address() == action_command.get([ns.META, ns.GATEWAY])[1]
    assert response.get_request_attribute('foo') == action_command.get([ns.META, ns.ATTRIBUTES, 'foo'])
    assert response.get_request_attributes() == action_command.get([ns.META, ns.ATTRIBUTES])
    assert isinstance(response.get_http_response(), HttpResponse)
    assert isinstance(response.get_http_request(), HttpRequest)
    assert response.has_return()
    assert isinstance(response.get_transport(), Transport)
    assert response.get_return() == 42


def test_response_http_defaults(state):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    state.context['command'] = CommandPayload()
    state.context['reply'] = ReplyPayload()

    response = Response(Middleware(), state)
    http_response = response.get_http_response()
    assert not http_response.is_protocol_version('2.0')
    assert http_response.get_protocol_version() == ''
    assert http_response.is_status('')
    assert http_response.get_status() == ''
    assert http_response.get_status_code() == 0
    assert http_response.get_status_text() == ''
    assert not http_response.has_header('fooh')
    assert http_response.get_header('fooh') == ''
    assert http_response.get_header_array('fooh') == []
    assert http_response.get_headers() == {}
    assert http_response.get_headers_array() == {}
    assert not http_response.has_body()
    assert http_response.get_body() == b''

    with pytest.raises(TypeError):
        http_response.get_header_array('fooh', 77)


def test_response_http(state, action_command, response_reply):
    from kusanagi.sdk import HttpResponse
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command
    state.context['reply'] = response_reply

    http_payload = response_reply.get([ns.RESPONSE])

    response = Response(Middleware(), state)
    http_response = response.get_http_response()

    assert http_response.is_protocol_version(http_payload.get(ns.VERSION))
    assert http_response.get_protocol_version() == http_payload.get(ns.VERSION)
    # Update the protocol version
    assert http_response.get_protocol_version() != '2.2'
    assert isinstance(http_response.set_protocol_version('2.2'), HttpResponse)
    assert http_response.get_protocol_version() == '2.2'

    assert http_response.is_status("418 I'm a teapot")
    assert http_response.get_status() == http_payload.get(ns.STATUS)
    assert http_response.get_status_code() == 418
    assert http_response.get_status_text() == "I'm a teapot"
    # Update the status
    assert isinstance(http_response.set_status(500, 'Internal Server Error'), HttpResponse)
    assert http_response.is_status('500 Internal Server Error')
    assert http_response.get_status() == '500 Internal Server Error'
    assert http_response.get_status_code() == 500
    assert http_response.get_status_text() == 'Internal Server Error'

    assert http_response.has_body()
    assert http_response.get_body() == http_payload.get(ns.BODY)
    # Update the body
    assert http_response.get_body() != b'blah'
    assert isinstance(http_response.set_body(b'blah'), HttpResponse)
    assert http_response.get_body() == b'blah'


def test_response_http_headers(state, action_command, response_reply):
    from kusanagi.sdk import HttpResponse
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Response
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = action_command
    state.context['reply'] = response_reply

    headers = response_reply.get([ns.RESPONSE, ns.HEADERS], {})

    response = Response(Middleware(), state)
    http_response = response.get_http_response()
    assert http_response.has_header('fooh')
    assert http_response.get_header('fooh') == headers.get('fooh')[0]
    assert http_response.get_header_array('fooh') == headers.get('fooh')
    assert http_response.get_headers() == {'fooh': headers.get('fooh')[0]}
    assert http_response.get_headers_array() == headers
    # The case is not checked when querying for existence
    assert http_response.has_header('Fooh')
    assert http_response.has_header('FOOH')
    assert http_response.has_header('FooH')

    # Add a new header
    assert not http_response.has_header('foo')
    assert isinstance(http_response.set_header('foo', 'bar'), HttpResponse)
    assert http_response.has_header('foo')
    assert http_response.get_header_array('foo') == ['bar']
    http_response.set_header('foo', 'baz')
    assert http_response.get_header_array('foo') == ['bar', 'baz']
    # Non string values are converted to string
    http_response.set_header('foo', 42)
    assert http_response.get_header_array('foo') == ['bar', 'baz', '42']
    # When the header name case is different it is updated
    assert 'foo' in http_response.get_headers()
    assert 'Foo' not in http_response.get_headers()
    http_response.set_header('Foo', 'blah')
    assert 'foo' not in http_response.get_headers()
    assert 'Foo' in http_response.get_headers()
    assert http_response.get_header('Foo') == 'bar'
    assert http_response.get_header_array('Foo') == ['bar', 'baz', '42', 'blah']
    # The header name is case insensitive while getting its values
    assert http_response.get_header('foo') == 'bar'
    assert http_response.get_header_array('foo') == ['bar', 'baz', '42', 'blah']

    # By default headers are not overwritten, but they can be ovewritten
    http_response.set_header('Foo', 'first', overwrite=True)
    assert http_response.get_header_array('foo') == ['first']
    # Headers can be ovewriten when a new name case is used
    assert 'foo' not in http_response.get_headers()
    http_response.set_header('foo', 'final', overwrite=True)
    assert http_response.get_header_array('foo') == ['final']
    assert 'foo' in http_response.get_headers()
