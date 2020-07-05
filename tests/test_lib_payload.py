# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_payload():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': 'baz'})
    assert isinstance(payload, dict)
    assert str(payload) == '{\n  "foo": "bar",\n  "bar": "baz"\n}'


def test_lib_payload_exists():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42}})
    assert payload.exists(['foo'])
    assert payload.exists(['bar', 'baz'])
    assert not payload.exists(['invalid', 'baz'])

    payload.path_prefix = ['bar']
    assert not payload.exists(['foo'])
    assert payload.exists(['baz'])


def test_lib_payload_equals():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42}})
    assert payload.equals(['bar', 'baz'], 42)
    # False is returned when the path is invalid
    assert not payload.equals(['invalid', 'baz'], '')

    payload.path_prefix = ['bar']
    assert not payload.equals(['bar', 'baz'], 42)
    assert payload.equals(['baz'], 42)


def test_lib_payload_get():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42}})
    assert payload.get(['bar', 'baz']) == 42
    assert payload.get(['invalid', 'baz']) is None
    assert payload.get(['invalid', 'baz'], 'default') == 'default'

    payload.path_prefix = ['bar']
    assert not payload.get(['bar', 'baz']) == 42
    assert payload.get(['baz']) == 42
    assert payload.get(['invalid', 'baz']) is None
    assert payload.get(['invalid', 'baz'], 'default') == 'default'


def test_lib_payload_set():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42, 'blah': []}})
    # Set value for an existing path
    assert payload.get(['bar', 'baz']) == 42
    assert payload.set(['bar', 'baz'], 77)
    assert payload.get(['bar', 'baz']) == 77
    # Set a value for a new path
    assert not payload.exists(['invalid', 'baz'])
    assert payload.set(['invalid', 'baz'], 77)
    assert payload.get(['invalid', 'baz']) == 77
    # Set value for an existing path that is not seteable
    assert payload.get(['bar', 'blah']) == []
    assert not payload.set(['bar', 'blah', 'teh'], 77)
    assert payload.get(['bar', 'blah']) == []

    assert payload.get(['bar', 'baz']) == 77
    payload.path_prefix = ['bar']
    assert payload.get(['baz']) == 77
    assert payload.set(['baz'], 42)
    assert payload.get(['baz']) == 42
    assert payload.get(['bar', 'baz'], prefix=False) == 42


def test_lib_payload_append():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42, 'blah': []}})
    assert payload.append(['bar', 'blah'], 1)
    assert payload.get(['bar', 'blah']) == [1]
    assert not payload.exists(['invalid', 'baz'])
    assert not payload.append(['bar', 'baz', 'boom'], 1)
    assert payload.get(['invalid', 'baz']) is None
    assert payload.append(['invalid', 'baz'], 2)
    assert payload.get(['invalid', 'baz']) == [2]

    payload.path_prefix = ['bar']
    assert payload.get(['blah']) == [1]
    assert payload.append(['blah'], 3)
    assert payload.get(['blah']) == [1, 3]


def test_lib_payload_extend():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42, 'blah': []}})
    assert payload.extend(['bar', 'blah'], [1])
    assert payload.get(['bar', 'blah']) == [1]
    assert not payload.extend(['bar', 'baz', 'boom'], [1])
    assert not payload.exists(['invalid', 'baz'])
    assert payload.get(['invalid', 'baz']) is None
    assert payload.extend(['invalid', 'baz'], [2])
    assert payload.get(['invalid', 'baz']) == [2]

    payload.path_prefix = ['bar']
    assert payload.get(['blah']) == [1]
    assert payload.extend(['blah'], [3])
    assert payload.get(['blah']) == [1, 3]


def test_lib_payload_delete():
    from kusanagi.sdk.lib.payload import Payload

    payload = Payload({'foo': 'bar', 'bar': {'baz': 42, 'blah': []}})
    assert not payload.delete(['invalid', 'baz'])
    assert not payload.delete(['bar', 'blah', 'boom'])
    assert payload.delete(['bar', 'blah'])
    assert not payload.exists(['bar', 'blah'])

    payload.path_prefix = ['bar']
    assert payload.exists(['baz'])
    assert payload.delete(['baz'])
    assert not payload.exists(['baz'])
