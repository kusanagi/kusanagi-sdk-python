# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_payload_error_defaults():
    from kusanagi.sdk.lib.payload.error import ErrorPayload

    payload = ErrorPayload()
    assert payload.get_message() == ErrorPayload.DEFAULT_MESSAGE
    assert payload.get_code() == 0
    assert payload.get_status() == ErrorPayload.DEFAULT_STATUS


def test_lib_payload_error():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.error import ErrorPayload

    payload = ErrorPayload.new('Message', 42, '419 Status')
    assert isinstance(payload, ErrorPayload)
    assert len(payload) == 1
    assert payload.exists([ns.ERROR], prefix=False)
    assert len(payload[ns.ERROR]) == 3
    assert payload.exists([ns.MESSAGE])
    assert payload.exists([ns.CODE])
    assert payload.exists([ns.STATUS])

    assert payload.get_message() == 'Message'
    assert payload.get_code() == 42
    assert payload.get_status() == '419 Status'
