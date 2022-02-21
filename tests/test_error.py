# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_error_defaults():
    from kusanagi.sdk import Error

    error = Error('http://1.2.3.4:77', 'foo', 'bar')
    assert error.get_address() == 'http://1.2.3.4:77'
    assert error.get_name() == 'foo'
    assert error.get_version() == 'bar'
    assert error.get_message() == Error.DEFAULT_MESSAGE
    assert error.get_code() == Error.DEFAULT_CODE
    assert error.get_status() == Error.DEFAULT_STATUS

    text = str(error)
    assert error.get_address() in text
    assert error.get_name() in text
    assert error.get_version() in text
    assert error.get_message() in text


def test_error():
    from kusanagi.sdk import Error

    error = Error('http://1.2.3.4:77', 'foo', 'bar', 'Message', 404, 'Not Found')
    assert error.get_address() == 'http://1.2.3.4:77'
    assert error.get_name() == 'foo'
    assert error.get_version() == 'bar'
    assert error.get_message() == 'Message'
    assert error.get_code() == 404
    assert error.get_status() == 'Not Found'

    text = str(error)
    assert error.get_address() in text
    assert error.get_name() in text
    assert error.get_version() in text
    assert error.get_message() in text
