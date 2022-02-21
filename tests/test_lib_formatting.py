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


def test_lib_str_to_datetime():
    from kusanagi.sdk.lib.formatting import str_to_datetime

    value = datetime(2017, 1, 27, 20, 12, 8, 952811)
    assert str_to_datetime('2017-01-27T20:12:08.952811+00:00') == value


def test_lib_datetime_to_str():
    from kusanagi.sdk.lib.formatting import datetime_to_str

    value = datetime(2017, 1, 27, 20, 12, 8, 952811)
    assert datetime_to_str(value) == '2017-01-27T20:12:08.952811+00:00'


def test_lib_str_to_date():
    from kusanagi.sdk.lib.formatting import str_to_date

    value = date(2017, 1, 27)
    assert str_to_date('2017-01-27') == value


def test_lib_date_to_str():
    from kusanagi.sdk.lib.formatting import date_to_str

    value = date(2017, 1, 27)
    assert date_to_str(value) == '2017-01-27'


def test_lib_time_to_str():
    from kusanagi.sdk.lib.formatting import time_to_str

    value = time.struct_time((0, 0, 0, 20, 12, 8, 0, 0, 0))
    assert time_to_str(value) == '20:12:08'
