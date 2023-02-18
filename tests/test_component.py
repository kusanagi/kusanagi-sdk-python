# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_component_resources(mocker):
    from kusanagi.sdk.component import Component

    resource_factory = mocker.Mock(return_value='bar')

    component = Component()
    assert not component.has_resource('foo')
    component.set_resource('foo', resource_factory)
    assert component.has_resource('foo')
    assert component.get_resource('foo') == 'bar'
    resource_factory.assert_called_once_with(component)

    # The factory must return a value
    with pytest.raises(ValueError):
        component.set_resource('bar', lambda *args: None)

    # Check that an exception is raised wen the resource doesn't exist
    with pytest.raises(LookupError):
        component.get_resource('invalid')


def test_component_log(logs):
    from kusanagi.sdk.component import Component
    from kusanagi.sdk.lib.logging import DEBUG

    component = Component()
    assert component.log('Test message', DEBUG) == component
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[DEBUG]' in output


def test_component_run(mocker):
    from kusanagi.sdk.component import Component

    server = mocker.Mock(return_value=None)
    server_factory = mocker.patch('kusanagi.sdk.component.create_server', return_value=server)
    startup_callback = mocker.Mock(return_value=None)
    shutdown_callback = mocker.Mock(return_value=None)
    error_callback = mocker.Mock(return_value=None)

    component = Component()
    component.startup(startup_callback)
    component.shutdown(shutdown_callback)
    component.error(error_callback)
    assert component.run()

    # The server factory is called with the component, the callbacks dict and the events error handler
    server_factory.asser_called_once()
    server_factory_args = server_factory.call_args[0]
    assert len(server_factory_args) == 3
    assert server_factory_args[0] == component
    # There are no callbacks so the callbacks dict must be empty
    assert isinstance(server_factory_args[1], dict)
    assert len(server_factory_args[1]) == 0

    server.start.assert_called_once()
    startup_callback.assert_called_once_with(component)
    shutdown_callback.assert_called_once_with(component)
    error_callback.assert_not_called()


def test_component_run_fail(mocker, logs):
    from kusanagi.sdk.component import Component

    error = Exception('boom!')
    mocker.patch('kusanagi.sdk.component.create_server', side_effect=error)
    startup_callback = mocker.Mock(return_value=None)
    shutdown_callback = mocker.Mock(return_value=None)
    error_callback = mocker.Mock(return_value=None)

    component = Component()
    component.startup(startup_callback)
    component.shutdown(shutdown_callback)
    component.error(error_callback)
    assert not component.run()

    startup_callback.assert_called_once_with(component)
    shutdown_callback.assert_called_once_with(component)
    # NOTE: The error callback is called when the server calls the userland
    #       callback and it fails. That case is tested in the server. Here is
    #       not called because the server is mocked.
    error_callback.assert_not_called()

    output = logs.getvalue()
    assert str(error) in output
