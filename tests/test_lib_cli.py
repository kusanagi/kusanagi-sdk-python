# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_lib_parse_args(mocker):
    from kusanagi.sdk.lib import logging
    from kusanagi.sdk.lib.cli import PARSER
    from kusanagi.sdk.lib.cli import parse_args

    mocker.patch('inspect.getouterframes', return_value=[['', 'test.py']])

    class Namespace(object):
        pass

    namespace = Namespace()
    namespace.component = 'service'
    namespace.name = 'foo'
    namespace.version = '1.0.0'
    namespace.framework_version = '3.0.0'
    namespace.socket = '@kusanagi-1.2.3.4-77'
    namespace.timeout = 10000
    namespace.debug = True
    namespace.var = ['foo=bar', 'bar=baz']
    namespace.tcp = None
    namespace.log_level = 7  # SYSLOG_NUMERIC[7] = DEBUG
    PARSER.parse_args = mocker.Mock(return_value=namespace)

    input_ = parse_args()
    assert input_.get_path() == 'test.py'
    assert input_.get_component() == 'service'
    assert input_.get_name() == 'foo'
    assert input_.get_version() == '1.0.0'
    assert input_.get_framework_version() == '3.0.0'
    assert input_.get_socket() == '@kusanagi-1.2.3.4-77'
    assert input_.get_tcp() == 0
    assert not input_.is_tcp_enabled()
    assert input_.get_channel() == 'ipc://@kusanagi-1.2.3.4-77'
    assert input_.get_timeout() == 10000
    assert input_.is_debug()
    assert input_.has_variable('foo')
    assert not input_.has_variable('invalid')
    assert input_.get_variable('foo') == 'bar'
    assert input_.get_variables() == {'foo': 'bar', 'bar': 'baz'}
    assert input_.has_logging()
    assert input_.get_log_level() == logging.DEBUG


def test_lib_parse_key_value_list():
    from kusanagi.sdk.lib.cli import parse_key_value_list

    assert parse_key_value_list([]) == {}
    assert parse_key_value_list(['foo=bar', 'bar=baz']) == {'foo': 'bar', 'bar': 'baz'}

    with pytest.raises(ValueError):
        parse_key_value_list([''])


def test_lib_input_ipc():
    from kusanagi.sdk.lib import logging
    from kusanagi.sdk.lib.cli import Input

    variables = {'foo': 'bar', 'bar': 'baz'}
    input_ = Input(
        'test.py',
        component='service',
        name='foo',
        version='1.0.0',
        framework_version='3.0.0',
        socket='@kusanagi-1.2.3.4-77',
        timeout=10000,
        debug=True,
        var=variables,
        tcp=None,
        log_level=7,  # SYSLOG_NUMERIC[7] = DEBUG
    )
    assert input_.get_path() == 'test.py'
    assert input_.get_component() == 'service'
    assert input_.get_name() == 'foo'
    assert input_.get_version() == '1.0.0'
    assert input_.get_framework_version() == '3.0.0'
    assert input_.get_socket() == '@kusanagi-1.2.3.4-77'
    assert input_.get_tcp() == 0
    assert not input_.is_tcp_enabled()
    assert input_.get_channel() == 'ipc://@kusanagi-1.2.3.4-77'
    assert input_.get_timeout() == 10000
    assert input_.is_debug()
    assert input_.has_variable('foo')
    assert not input_.has_variable('invalid')
    assert input_.get_variable('foo') == 'bar'
    assert input_.get_variables() == variables
    assert input_.has_logging()
    assert input_.get_log_level() == logging.DEBUG


def test_lib_input_ipc_default():
    from kusanagi.sdk.lib import logging
    from kusanagi.sdk.lib.cli import Input

    variables = {'foo': 'bar', 'bar': 'baz'}
    input_ = Input(
        'test.py',
        component='service',
        name='foo',
        version='1.0.0',
        framework_version='3.0.0',
        socket=None,
        timeout=10000,
        debug=True,
        var=variables,
        tcp=None,
        log_level=7,  # SYSLOG_NUMERIC[7] = DEBUG
    )

    assert input_.get_path() == 'test.py'
    assert input_.get_component() == 'service'
    assert input_.get_name() == 'foo'
    assert input_.get_version() == '1.0.0'
    assert input_.get_framework_version() == '3.0.0'
    assert input_.get_socket() == '@kusanagi-service-foo-1-0-0'
    assert input_.get_tcp() == 0
    assert not input_.is_tcp_enabled()
    assert input_.get_channel() == 'ipc://@kusanagi-service-foo-1-0-0'
    assert input_.get_timeout() == 10000
    assert input_.is_debug()
    assert input_.has_variable('foo')
    assert not input_.has_variable('invalid')
    assert input_.get_variable('foo') == 'bar'
    assert input_.get_variables() == variables
    assert input_.has_logging()
    assert input_.get_log_level() == logging.DEBUG


def test_lib_input_tcp():
    from kusanagi.sdk.lib import logging
    from kusanagi.sdk.lib.cli import Input

    variables = {'foo': 'bar', 'bar': 'baz'}
    input_ = Input(
        'test.py',
        component='service',
        name='foo',
        version='1.0.0',
        framework_version='3.0.0',
        socket=None,
        timeout=10000,
        debug=True,
        var=variables,
        tcp=77,
        log_level=7,  # SYSLOG_NUMERIC[7] = DEBUG
    )
    assert input_.get_path() == 'test.py'
    assert input_.get_component() == 'service'
    assert input_.get_name() == 'foo'
    assert input_.get_version() == '1.0.0'
    assert input_.get_framework_version() == '3.0.0'
    assert input_.get_socket() == ''
    assert input_.get_tcp() == 77
    assert input_.is_tcp_enabled()
    assert input_.get_channel() == 'tcp://127.0.0.1:77'
    assert input_.get_timeout() == 10000
    assert input_.is_debug()
    assert input_.has_variable('foo')
    assert not input_.has_variable('invalid')
    assert input_.get_variable('foo') == 'bar'
    assert input_.get_variables() == variables
    assert input_.has_logging()
    assert input_.get_log_level() == logging.DEBUG
