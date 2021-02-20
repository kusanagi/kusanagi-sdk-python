# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from datetime import date
from datetime import datetime
from decimal import Decimal

import pytest


def test_lib_json_encoder():
    from kusanagi.sdk.lib.json import Encoder

    encoder = Encoder()
    assert encoder.default(Decimal('123.321')) == '123.321'
    assert encoder.default(date(2017, 1, 27)) == '2017-01-27'
    assert encoder.default(datetime(2017, 1, 27, 20, 12, 8, 952811)) == '2017-01-27T20:12:08.952811+00:00'
    assert encoder.default(b'value') == 'value'

    # Unknown objects should raise an error
    with pytest.raises(TypeError):
        encoder.default(object())


def test_lib_json_loads():
    from kusanagi.sdk.lib.json import loads

    assert loads('"text"') == 'text'
    assert loads('{"foo": "bar"}') == {'foo': 'bar'}


def test_lib_json_dumps():
    from kusanagi.sdk.lib.json import dumps

    assert dumps('text') == b'"text"'
    assert dumps({'foo': 'bar'}) == b'{"foo":"bar"}'
    assert dumps([1, 2, 3]) == b'[1,2,3]'


def test_lib_json_dumps_pretty():
    from kusanagi.sdk.lib.json import dumps

    assert dumps('text', prettify=True) == b'"text"'
    assert dumps({'foo': 'bar'}, prettify=True) == b'{\n  "foo": "bar"\n}'
    assert dumps([1, 2, 3], prettify=True) == b'[\n  1,\n  2,\n  3\n]'
