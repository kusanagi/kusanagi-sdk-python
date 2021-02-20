# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import sys

import pytest


def test_param_defaults():
    from kusanagi.sdk import Param

    param = Param('foo')
    assert param.get_name() == 'foo'
    assert param.get_value() == ''
    assert param.get_type() == Param.TYPE_STRING
    assert not param.exists()


def test_param():
    from kusanagi.sdk import Param

    param = Param('foo', 42, Param.TYPE_INTEGER, True)
    assert param.get_name() == 'foo'
    assert param.get_value() == 42
    assert param.get_type() == Param.TYPE_INTEGER
    assert param.exists()


def test_param_guess_type():
    from kusanagi.sdk import Param

    param = Param('foo', False, type=None)
    assert param.get_name() == 'foo'
    assert param.get_value() is False
    assert param.get_type() == Param.TYPE_BOOLEAN
    assert not param.exists()

    param = Param('foo', None, type=None)
    assert param.get_name() == 'foo'
    assert param.get_value() is None
    assert param.get_type() == Param.TYPE_NULL
    assert not param.exists()

    param = Param('foo', (1, 2), type=None)
    assert param.get_name() == 'foo'
    assert param.get_value() == [1, 2]
    assert param.get_type() == Param.TYPE_ARRAY
    assert not param.exists()

    # Unsupported value types without a type resolves to a string
    param = Param('foo', lambda: None, type=None)
    assert param.get_name() == 'foo'
    assert isinstance(param.get_value(), str)
    assert param.get_value().startswith('<function')
    assert param.get_type() == Param.TYPE_STRING
    assert not param.exists()


def test_param_invalid_type(logs):
    from kusanagi.sdk import Param

    param = Param('foo', False, 'INVALID')
    assert param.get_name() == 'foo'
    assert param.get_value() == ''
    assert param.get_type() == Param.TYPE_STRING
    assert not param.exists()
    # Check that the warning log exists
    output = logs.getvalue()
    assert '"foo"' in output
    assert '"INVALID"' in output


def test_param_invalid_value_type():
    from kusanagi.sdk import Param

    with pytest.raises(TypeError):
        Param('foo', 42, Param.TYPE_ARRAY)

    with pytest.raises(TypeError):
        Param('foo', 42, Param.TYPE_NULL)


def test_param_copy():
    from kusanagi.sdk import Param

    param = Param('foo', 42, Param.TYPE_INTEGER, True)
    new_param = param.copy_with_name('bar')
    assert new_param.get_name() == 'bar'
    assert new_param.get_value() == param.get_value()
    assert new_param.get_type() == param.get_type()
    assert new_param.exists() == param.exists()

    new_param = param.copy_with_value(77)
    assert new_param.get_value() == 77
    assert new_param.get_name() == param.get_name()
    assert new_param.get_type() == param.get_type()
    assert new_param.exists() == param.exists()

    new_param = param.copy_with_type(Param.TYPE_STRING)
    assert new_param.get_type() == Param.TYPE_STRING
    assert new_param.get_value() == '42'
    assert new_param.get_name() == param.get_name()
    assert new_param.exists() == param.exists()


def test_param_copy_fail():
    from kusanagi.sdk import Param

    param = Param('foo', 42, Param.TYPE_INTEGER, True)
    with pytest.raises(ValueError):
        param.copy_with_type('INVALID')

    with pytest.raises(TypeError):
        param.copy_with_type(Param.TYPE_ARRAY)


def test_param_schema_defaults():
    from kusanagi.sdk import HttpParamSchema
    from kusanagi.sdk import Param
    from kusanagi.sdk import ParamSchema
    from kusanagi.sdk.lib.payload.param import ParamSchemaPayload

    schema = ParamSchema(ParamSchemaPayload('foo'))
    assert schema.get_name() == 'foo'
    assert schema.get_type() == Param.TYPE_STRING
    assert schema.get_format() == ''
    assert schema.get_array_format() == ''
    assert schema.get_pattern() == ''
    assert not schema.allow_empty()
    assert not schema.has_default_value()
    assert schema.get_default_value() is None
    assert not schema.is_required()
    assert schema.get_items() == {}
    assert schema.get_max() == sys.maxsize
    assert not schema.is_exclusive_max()
    assert schema.get_min() == -sys.maxsize - 1
    assert not schema.is_exclusive_min()
    assert schema.get_max_items() == -1
    assert schema.get_min_items() == -1
    assert not schema.has_unique_items()
    assert schema.get_enum() == []
    assert schema.get_multiple_of() == -1

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpParamSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_input() == 'query'
    assert http_schema.get_param() == schema.get_name()


def test_param_schema():
    from kusanagi.sdk import HttpParamSchema
    from kusanagi.sdk import Param
    from kusanagi.sdk import ParamSchema
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.param import ParamSchemaPayload

    payload = {
        ns.TYPE: Param.TYPE_INTEGER,
        ns.FORMAT: 'email',
        ns.PATTERN: 'foo.*',
        ns.ALLOW_EMPTY: True,
        ns.DEFAULT_VALUE: 42,
        ns.REQUIRED: True,
        ns.MAX: 100444,
        ns.EXCLUSIVE_MAX: True,
        ns.MIN: 100,
        ns.EXCLUSIVE_MIN: True,
        ns.ENUM: [77, 41, 0],
        ns.MULTIPLE_OF: 6,
        ns.HTTP: {
            ns.GATEWAY: False,
            ns.INPUT: 'path',
            ns.PARAM: 'bar',
        }
    }

    schema = ParamSchema(ParamSchemaPayload('foo', payload))
    assert schema.get_name() == 'foo'
    assert schema.get_type() == payload[ns.TYPE]
    assert schema.get_format() == payload[ns.FORMAT]
    assert schema.get_array_format() == ''
    assert schema.get_pattern() == payload[ns.PATTERN]
    assert schema.allow_empty()
    assert schema.has_default_value()
    assert schema.get_default_value() == payload[ns.DEFAULT_VALUE]
    assert schema.is_required()
    assert schema.get_items() == {}
    assert schema.get_max() == payload[ns.MAX]
    assert schema.is_exclusive_max()
    assert schema.get_min() == payload[ns.MIN]
    assert schema.is_exclusive_min()
    assert schema.get_max_items() == -1
    assert schema.get_min_items() == -1
    assert not schema.has_unique_items()
    assert schema.get_enum() == payload[ns.ENUM]
    assert schema.get_multiple_of() == payload[ns.MULTIPLE_OF]

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpParamSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_input() == payload[ns.HTTP][ns.INPUT]
    assert http_schema.get_param() == payload[ns.HTTP][ns.PARAM]


def test_param_schema_array():
    from kusanagi.sdk import Param
    from kusanagi.sdk import ParamSchema
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.param import ParamSchemaPayload

    payload = {
        ns.TYPE: Param.TYPE_ARRAY,
        ns.ARRAY_FORMAT: ParamSchema.ARRAY_FORMAT_CSV,
        ns.ITEMS: {'type': 'array'},
        ns.MAX_ITEMS: 4,
        ns.MIN_ITEMS: 1,
        ns.UNIQUE_ITEMS: True,
    }

    schema = ParamSchema(ParamSchemaPayload('foo', payload))
    assert schema.get_type() == payload[ns.TYPE]
    assert schema.get_array_format() == payload[ns.ARRAY_FORMAT]
    assert schema.get_items() == payload[ns.ITEMS]
    assert schema.get_max_items() == payload[ns.MAX_ITEMS]
    assert schema.get_min_items() == payload[ns.MIN_ITEMS]
    assert schema.has_unique_items()


def test_validate_param_list():
    from kusanagi.sdk import Param
    from kusanagi.sdk.param import validate_parameter_list

    assert validate_parameter_list([]) is None
    assert validate_parameter_list([Param('a'), Param('b')]) is None

    with pytest.raises(ValueError):
        assert validate_parameter_list([Param('a'), 'boom!']) is None
