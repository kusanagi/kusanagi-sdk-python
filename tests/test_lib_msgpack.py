# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import time
from datetime import date
from datetime import datetime
from decimal import Decimal

import pytest


def test_lib_msgpack_encode():
    from kusanagi.sdk.lib.msgpack import _encode

    time_value = '20:12:08'
    date_value = '2017-01-27'
    datetime_value = f'{date_value}T{time_value}.952811+00:00'

    assert _encode(Decimal('123.321')) == ['type', 'decimal', ['123', '321']]
    assert _encode(date(2017, 1, 27)) == ['type', 'date', date_value]
    assert _encode(datetime(2017, 1, 27, 20, 12, 8, 952811)) == ['type', 'datetime', datetime_value]
    assert _encode(time.strptime("2017-01-27 20:12:08", "%Y-%m-%d %H:%M:%S")) == ['type', 'time', time_value]

    # A string is not a custom type
    with pytest.raises(TypeError):
        _encode('')


def test_lib_msgpack_decode():
    from kusanagi.sdk.lib.msgpack import _decode

    time_value = '20:12:08'
    date_value = '2017-01-27'
    datetime_value = f'{date_value}T{time_value}.952811+00:00'

    assert _decode(['type', 'decimal', ['123', '321']]) == Decimal('123.321')
    assert _decode(['type', 'date', date_value]) == date(2017, 1, 27)
    assert _decode(['type', 'datetime', datetime_value]) == datetime(2017, 1, 27, 20, 12, 8, 952811)
    assert _decode(['type', 'time', time_value]) == time_value

    # Invalid format should not fail
    assert _decode(['type', 'date', '']) is None

    # Values other than dictionaries are not decoded
    assert _decode('NON_DICT') == 'NON_DICT'


def test_lib_msgpack_pack():
    from kusanagi.sdk.lib.msgpack import pack

    assert pack({}) == b'\x80'


def test_lib_msgpack_unpack():
    from kusanagi.sdk.lib.msgpack import unpack

    assert unpack(b'\x80') == {}
