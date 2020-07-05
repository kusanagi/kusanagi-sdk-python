# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import os

import pytest


def test_api(state):
    from kusanagi.sdk import Service
    from kusanagi.sdk.api import Api

    component = Service()
    component.set_resource('foo', lambda *args: 'bar')

    api = Api(component, state)
    assert api.is_debug()
    assert api.get_framework_version() == state.values.get_framework_version()
    assert api.get_path() == os.path.dirname(state.values.get_path())
    assert api.get_name() == state.values.get_name()
    assert api.get_version() == state.values.get_version()
    assert not api.has_variable('invalid')
    assert api.has_variable('foo')
    assert api.get_variable('foo') == 'bar'
    assert 'foo' in api.get_variables()
    assert api.has_resource('foo')
    assert api.get_resource('foo') == 'bar'

    with pytest.raises(Exception):
        api.done()


def test_api_log(state, logs):
    from kusanagi.sdk import Service
    from kusanagi.sdk.api import Api
    from kusanagi.sdk.lib.logging import DEBUG

    api = Api(Service(), state)
    assert api.log('Test message', DEBUG) == api
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[DEBUG]' in output


def test_api_service_schema(state, logs, schemas):
    from kusanagi.sdk import Service
    from kusanagi.sdk import ServiceSchema
    from kusanagi.sdk.api import Api

    state.context['schemas'] = schemas

    api = Api(Service(), state)
    assert api.get_services() == [{'name': 'foo', 'version': '1.0.0'}]

    service_schema = api.get_service_schema('foo', '1.0.0')
    assert isinstance(service_schema, ServiceSchema)

    with pytest.raises(LookupError):
        api.get_service_schema('invalid', '1.0.0')
