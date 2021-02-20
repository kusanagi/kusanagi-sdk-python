# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from urllib.parse import urlparse

import pytest


def test_request_defaults(state):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    state.context['command'] = CommandPayload()
    state.context['reply'] = ReplyPayload()

    request = Request(Middleware(), state)
    assert request.get_id() == ''
    assert request.get_timestamp() == ''
    assert request.get_gateway_protocol() == ''
    assert request.get_gateway_address() == ''
    assert request.get_client_address() == ''
    assert request.get_service_name() == ''
    assert request.get_service_version() == ''
    assert request.get_action_name() == ''


def test_request_http_defaults(state):
    from kusanagi.sdk import File
    from kusanagi.sdk import HttpRequest
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload.command import CommandPayload
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    state.context['reply'] = ReplyPayload()

    state.context['command'] = CommandPayload()

    request = Request(Middleware(), state)
    http_request = request.get_http_request()
    assert isinstance(http_request, HttpRequest)
    assert not http_request.is_method('POST')
    assert http_request.get_method() == ''
    assert http_request.get_url() == ''
    assert http_request.get_url_scheme() == ''
    assert http_request.get_url_host() == ''
    assert http_request.get_url_port() == 0
    assert http_request.get_url_path() == ''
    assert not http_request.has_query_param('foo')
    assert http_request.get_query_param('foo') == ''
    assert http_request.get_query_param_array('foo') == []
    assert http_request.get_query_params() == {}
    assert http_request.get_query_params_array() == {}
    assert not http_request.has_post_param('foo')
    assert http_request.get_post_param('foo') == ''
    assert http_request.get_post_param_array('foo') == []
    assert http_request.get_post_params() == {}
    assert http_request.get_post_params_array() == {}
    assert not http_request.is_protocol_version('1.2')
    assert http_request.get_protocol_version() == ''
    assert not http_request.has_header('foo')
    assert http_request.get_header('foo') == ''
    assert http_request.get_header_array('foo') == []
    assert http_request.get_headers() == {}
    assert http_request.get_headers_array() == {}
    assert not http_request.has_body()
    assert http_request.get_body() == b''
    assert not http_request.has_file('foo')
    file = http_request.get_file('foo')
    assert isinstance(file, File)
    assert file.get_name() == 'foo'
    assert http_request.get_files() == []

    with pytest.raises(TypeError):
        http_request.get_query_param_array('foo', 42)

    with pytest.raises(TypeError):
        http_request.get_post_param_array('foo', 42)

    with pytest.raises(TypeError):
        http_request.get_header_array('foo', 42)


def test_request(state, command, reply):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload import ns

    state.context['command'] = command
    state.context['reply'] = reply

    request = Request(Middleware(), state)
    assert request.get_id() == command.get([ns.META, ns.ID])
    assert request.get_timestamp() == command.get([ns.META, ns.DATETIME])
    assert request.get_gateway_protocol() == command.get([ns.META, ns.PROTOCOL])
    assert request.get_gateway_address() == command.get([ns.META, ns.GATEWAY])[1]
    assert request.get_client_address() == command.get([ns.META, ns.CLIENT])
    assert request.get_service_name() == reply.get([ns.CALL, ns.SERVICE])
    assert request.get_service_version() == reply.get([ns.CALL, ns.VERSION])
    assert request.get_action_name() == reply.get([ns.CALL, ns.ACTION])

    assert isinstance(request.set_service_name('baz'), Request)
    assert request.get_service_name() == 'baz'
    assert isinstance(request.set_service_version('3.2.1'), Request)
    assert request.get_service_version() == '3.2.1'
    assert isinstance(request.set_action_name('blahz'), Request)
    assert request.get_action_name() == 'blahz'


def test_request_http(state, command):
    from kusanagi.sdk import File
    from kusanagi.sdk import HttpRequest
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    state.context['reply'] = ReplyPayload()
    state.context['command'] = command

    http_payload = command.get([ns.REQUEST])
    method = http_payload.get(ns.METHOD)
    url = urlparse(http_payload.get(ns.URL, ''))

    request = Request(Middleware(), state)
    http_request = request.get_http_request()
    assert isinstance(http_request, HttpRequest)
    assert http_request.is_method(method)
    assert http_request.get_method() == method
    assert http_request.get_url() == http_payload.get(ns.URL)
    assert http_request.get_url_scheme() == url.scheme
    assert http_request.get_url_host() == url.netloc.split(':')[0]
    assert http_request.get_url_port() == url.port
    assert http_request.get_url_path() == url.path.rstrip('/')
    assert http_request.has_query_param('fooq')
    assert http_request.get_query_param('fooq') == 'barq'
    assert http_request.get_query_param_array('fooq') == ['barq', 'bazq']
    assert http_request.get_query_params() == {'fooq': 'barq'}
    assert http_request.get_query_params_array() == {'fooq': ['barq', 'bazq']}
    assert http_request.has_post_param('foop')
    assert http_request.get_post_param('foop') == 'barp'
    assert http_request.get_post_param_array('foop') == ['barp', 'bazp']
    assert http_request.get_post_params() == {'foop': 'barp'}
    assert http_request.get_post_params_array() == {'foop': ['barp', 'bazp']}
    assert http_request.is_protocol_version('2.0')
    assert http_request.get_protocol_version() == '2.0'
    assert http_request.has_header('fooh')
    assert http_request.get_header('fooh') == 'barh'
    assert http_request.get_header_array('fooh') == ['barh', 'bazh']
    assert http_request.get_headers() == {'fooh': 'barh'}
    assert http_request.get_headers_array() == {'fooh': ['barh', 'bazh']}
    assert http_request.has_body()
    assert http_request.get_body() == http_payload.get(ns.BODY)
    assert http_request.has_file('foof')
    file = http_request.get_file('foof')
    assert isinstance(file, File)
    assert file.get_name() == 'foof'
    files = http_request.get_files()
    assert len(files) == 1
    assert isinstance(files[0], File)
    assert files[0].get_name() == 'foof'


def test_request_attributes(state):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload()
    state.context['reply'] = reply

    request = Request(Middleware(), state)
    assert not reply.exists([ns.ATTRIBUTES, 'foo'])
    request.set_attribute('foo', 'bar')
    assert reply.exists([ns.ATTRIBUTES, 'foo'])
    assert reply.get([ns.ATTRIBUTES, 'foo']) == 'bar'

    # Attribute values must be strings
    with pytest.raises(TypeError):
        request.set_attribute('bar', 77)


def test_request_params(state):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Param
    from kusanagi.sdk import Request
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload()
    reply.set([ns.CALL, ns.PARAMS], [{ns.NAME: 'foo'}])
    state.context['reply'] = reply
    request = Request(Middleware(), state)

    # Check for a valid parameter
    assert request.has_param('foo')
    param = request.get_param('foo')
    assert isinstance(param, Param)
    assert param.get_name() == 'foo'
    # Add a new parameter
    param = request.new_param('bar', 42)
    assert isinstance(request.set_param(param), Request)
    assert request.get_param('bar').get_value() == 42
    # List the parameters
    params = request.get_params()
    assert isinstance(params, list)
    assert len(params) == 2
    # Check that the last parameter is the one just added
    assert params[1].get_name() == param.get_name()
    assert params[1].get_value() == param.get_value()

    # Check for an invalid parameter
    assert not request.has_param('invalid')
    # When a parameter doesn't exists it is created but not added to the parameter list
    param = request.get_param('invalid')
    assert isinstance(param, Param)
    assert param.get_name() == 'invalid'
    assert len(request.get_params()) == 2


def test_request_response(state):
    from kusanagi.sdk import Middleware
    from kusanagi.sdk import Request
    from kusanagi.sdk import Response
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload()
    state.context['reply'] = reply
    request = Request(Middleware(), state)

    # Create a response with default values
    response = request.new_response()
    assert isinstance(response, Response)
    assert reply.exists([ns.RESPONSE])
    http_response = response.get_http_response()
    assert http_response.get_status_code() == request.DEFAULT_RESPONSE_STATUS_CODE
    assert http_response.get_status_text() == request.DEFAULT_RESPONSE_STATUS_TEXT

    # Create a response with custom values
    response = request.new_response(418, "I'm a teapot")
    assert isinstance(response, Response)
    assert reply.exists([ns.RESPONSE])
    http_response = response.get_http_response()
    assert http_response.get_status_code() == 418
    assert http_response.get_status_text() == "I'm a teapot"
