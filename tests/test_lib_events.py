# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_events_startup(mocker, logs):
    from kusanagi.sdk.lib.events import Events

    component = object()
    startup_callback = mocker.Mock(return_value=None)
    shutdown_callback = mocker.Mock(return_value=None)
    error_callback = mocker.Mock(return_value=None)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert events.startup(component)
    startup_callback.assert_called_once_with(component)
    shutdown_callback.assert_not_called()
    error_callback.assert_not_called()

    startup_callback = mocker.Mock(side_effect=Exception)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert not events.startup(component)
    startup_callback.assert_called_once_with(component)
    shutdown_callback.assert_not_called()
    error_callback.assert_not_called()

    assert logs.getvalue() != ''


def test_lib_events_shutdown(mocker, logs):
    from kusanagi.sdk.lib.events import Events

    component = object()
    startup_callback = mocker.Mock(return_value=None)
    shutdown_callback = mocker.Mock(return_value=None)
    error_callback = mocker.Mock(return_value=None)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert events.shutdown(component)
    startup_callback.assert_not_called()
    shutdown_callback.assert_called_once_with(component)
    error_callback.assert_not_called()

    shutdown_callback = mocker.Mock(side_effect=Exception)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert not events.shutdown(component)
    startup_callback.assert_not_called()
    shutdown_callback.assert_called_once_with(component)
    error_callback.assert_not_called()

    assert logs.getvalue() != ''


def test_lib_events_error(mocker, logs):
    from kusanagi.sdk.lib.events import Events

    error = object()
    startup_callback = mocker.Mock(return_value=None)
    shutdown_callback = mocker.Mock(return_value=None)
    error_callback = mocker.Mock(return_value=None)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert events.error(error)
    startup_callback.assert_not_called()
    shutdown_callback.assert_not_called()
    error_callback.assert_called_once_with(error)

    error_callback = mocker.Mock(side_effect=Exception)
    events = Events(startup_callback, shutdown_callback, error_callback)
    assert not events.error(error)
    startup_callback.assert_not_called()
    shutdown_callback.assert_not_called()
    error_callback.assert_called_once_with(error)

    assert logs.getvalue() != ''
