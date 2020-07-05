# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from .lib import datatypes
from .lib.payload import ns

if TYPE_CHECKING:
    from typing import Any
    from typing import List

    from .lib.payload.param import HttpParamSchemaPayload
    from .lib.payload.param import ParamSchemaPayload

LOG = logging.getLogger(__name__)


class Param(object):
    """
    Input parameter.

    Actions receive parameters thought calls to a service component.

    """

    TYPE_NULL = datatypes.TYPE_NULL
    TYPE_BOOLEAN = datatypes.TYPE_BOOLEAN
    TYPE_INTEGER = datatypes.TYPE_INTEGER
    TYPE_FLOAT = datatypes.TYPE_FLOAT
    TYPE_ARRAY = datatypes.TYPE_ARRAY
    TYPE_OBJECT = datatypes.TYPE_OBJECT
    TYPE_STRING = datatypes.TYPE_STRING
    TYPE_BINARY = datatypes.TYPE_BINARY

    def __init__(self, name: str, value: Any = '', type: str = '', exists: bool = False):
        """
        Constructor.

        :param name: Name of the parameter.
        :param value: Optional value for the parameter.
        :param type: Optional type for the parameter value.
        :param exists: Optional flag to know if the parameter exists in the service call.

        :raises: TypeError

        """

        if not type:
            type = resolve_param_type(value)
            if type == self.TYPE_ARRAY and isinstance(value, (tuple, set)):
                # Make sure the value is an list
                value = list(value)
            elif type == self.TYPE_STRING and not isinstance(value, str):
                # Make sure that the value is a string value
                value = str(value)
        elif type not in datatypes.TYPE_CHOICES:
            # Invalid parameter types are treated as string parameters
            LOG.warning(f'Invalid type for parameter "{name}", using string type: "{type}"')
            type = self.TYPE_STRING
            value = ''

        # Check that the value respects the parameter type
        if type == self.TYPE_NULL:
            if value is not None:
                raise TypeError('Value must be null')
        else:
            type_cls = TYPE_CLASSES[type]
            if not isinstance(value, type_cls):
                raise TypeError(f'Value must be {type}')

        self.__name = name
        self.__value = value
        self.__type = type
        self.__exists = exists

    def get_name(self) -> str:
        """Get the name of the parameter."""

        return self.__name

    def get_type(self) -> str:
        """Get the type of the parameter value."""

        return self.__type

    def get_value(self) -> Any:
        """Get the parameter value."""

        return self.__value

    def exists(self) -> bool:
        """Check if the parameter exists in the service call."""

        return self.__exists

    def copy_with_name(self, name: str) -> Param:
        """
        Copy the parameter with a new name.

        :param name: Name of the new parameter.

        """

        return self.__class__(name, value=self.__value, type=self.__type, exists=self.exists())

    def copy_with_value(self, value: Any) -> Param:
        """
        Copy the parameter with a new value.

        :param value: Value for the new parameter.

        """

        return self.__class__(self.__name, value=value, type=self.__type, exists=self.exists())

    def copy_with_type(self, type: str) -> Param:
        """
        Copy the parameter with a new type.

        :param type: Type for the new parameter.

        :raises: TypeError, ValueError

        """

        name = self.get_name()
        if type not in TYPE_CLASSES:
            raise ValueError(f'Param "{name}" copy failed because the type is invalid: "{type}"')

        # cast the value to the new type
        try:
            value = TYPE_CLASSES[type](self.get_value())
        except TypeError:
            current = self.get_type()
            raise TypeError(f'Param "{name}" copy failed: Type "{type}" is not compatible with "{current}"')

        return self.__class__(self.__name, value=value, type=type, exists=self.exists())


# Parameter type names to python types
TYPE_CLASSES = {
    Param.TYPE_BOOLEAN: bool,
    Param.TYPE_INTEGER: int,
    Param.TYPE_FLOAT: float,
    Param.TYPE_ARRAY: list,
    Param.TYPE_OBJECT: dict,
    Param.TYPE_STRING: str,
    Param.TYPE_BINARY: bytes,
}


def resolve_param_type(value: Any) -> str:
    """
    Resolves the parameter type to use for native python types.

    :param value: The value from where to resolve the type name.

    """

    if value is None:
        return Param.TYPE_NULL

    value_cls = value.__class__

    # Resolve non mapped types
    if value_cls in (tuple, set):
        return Param.TYPE_ARRAY

    # Resolve the mapped python types
    for type_name, cls in TYPE_CLASSES.items():
        if value_cls == cls:
            return type_name

    return Param.TYPE_STRING


class ParamSchema(object):
    """Parameter schema in the framework."""

    ARRAY_FORMAT_CSV = 'csv'
    ARRAY_FORMAT_SSV = 'ssv'
    ARRAY_FORMAT_TSV = 'tsv'
    ARRAY_FORMAT_PIPES = 'pipes'
    ARRAY_FORMAT_MULTI = 'multi'

    def __init__(self, payload: ParamSchemaPayload):
        self.__payload = payload

    def get_name(self) -> str:
        """Get parameter name."""

        return self.__payload.get_name()

    def get_type(self) -> str:
        """Get parameter value type."""

        return self.__payload.get([ns.TYPE], Param.TYPE_STRING)

    def get_format(self) -> str:
        """Get parameter value format."""

        return self.__payload.get([ns.FORMAT], '')

    def get_array_format(self) -> str:
        """
        Get format for the parameter if the type property is set to "array".

        An empty string is returned when the parameter type is not "array".

        Formats:
          - "csv" for comma separated values (default)
          - "ssv" for space separated values
          - "tsv" for tab separated values
          - "pipes" for pipe separated values
          - "multi" for multiple parameter instances instead of multiple values for a single instance.

        """

        if self.get_type() != Param.TYPE_ARRAY:
            return ''

        return self.__payload.get([ns.ARRAY_FORMAT], self.ARRAY_FORMAT_CSV)

    def get_pattern(self) -> str:
        """Get ECMA 262 compliant regular expression to validate the parameter."""

        return self.__payload.get([ns.PATTERN], '')

    def allow_empty(self) -> bool:
        """Check if the parameter allows an empty value."""

        return self.__payload.get([ns.ALLOW_EMPTY], False)

    def has_default_value(self) -> bool:
        """Check if the parameter has a default value defined."""

        return self.__payload.exists([ns.DEFAULT_VALUE])

    def get_default_value(self) -> Any:
        """Get default value for parameter."""

        return self.__payload.get([ns.DEFAULT_VALUE])

    def is_required(self) -> bool:
        """Check if parameter is required."""

        return self.__payload.get([ns.REQUIRED], False)

    def get_items(self) -> dict:
        """
        Get JSON schema with items object definition.

        An empty dictionary is returned when parameter is not an "array",
        otherwise the result contains a dictionary with a JSON schema definition.

        """

        if self.get_type() != Param.TYPE_ARRAY:
            return {}

        return self.__payload.get([ns.ITEMS], {})

    def get_max(self) -> int:
        """Get maximum value for parameter."""

        return self.__payload.get([ns.MAX], sys.maxsize)

    def is_exclusive_max(self) -> bool:
        """
        Check if max value is inclusive.

        When max is not defined inclusive is False.

        """

        if not self.__payload.exists([ns.MAX]):
            return False

        return self.__payload.get([ns.EXCLUSIVE_MAX], False)

    def get_min(self) -> int:
        """Get minimum value for parameter."""

        return self.__payload.get([ns.MIN], -sys.maxsize - 1)

    def is_exclusive_min(self) -> bool:
        """
        Check if minimum value is inclusive.

        When min is not defined inclusive is False.

        """

        if not self.__payload.exists([ns.MIN]):
            return False

        return self.__payload.get([ns.EXCLUSIVE_MIN], False)

    def get_max_items(self) -> int:
        """
        Get maximum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        """

        if self.get_type() != Param.TYPE_ARRAY:
            return -1

        return self.__payload.get([ns.MAX_ITEMS], -1)

    def get_min_items(self) -> int:
        """
        Get minimum number of items allowed for the parameter.

        Result is -1 when type is not "array" or values is not defined.

        """

        if self.get_type() != Param.TYPE_ARRAY:
            return -1

        return self.__payload.get([ns.MIN_ITEMS], -1)

    def has_unique_items(self) -> bool:
        """Check if param must contain a set of unique items."""

        return self.__payload.get([ns.UNIQUE_ITEMS], False)

    def get_enum(self) -> list:
        """Get the set of unique values that parameter allows."""

        return self.__payload.get([ns.ENUM], [])

    def get_multiple_of(self) -> int:
        """
        Get value that parameter must be divisible by.

        Result is -1 when this property is not defined.

        """

        return self.__payload.get([ns.MULTIPLE_OF], -1)

    def get_http_schema(self) -> HttpParamSchema:
        """Get HTTP param schema."""

        payload = self.__payload.get_http_param_schema_payload()
        return HttpParamSchema(payload)


class HttpParamSchema(object):
    """HTTP semantics of a parameter schema in the framework."""

    def __init__(self, payload: HttpParamSchemaPayload):
        self.__payload = payload

    def is_accessible(self) -> bool:
        """Check if the Gateway has access to the parameter."""

        return self.__payload.get([ns.GATEWAY], True)

    def get_input(self) -> str:
        """Get location of the parameter."""

        return self.__payload.get([ns.INPUT], 'query')

    def get_param(self) -> str:
        """Get name as specified via HTTP to be mapped to the name property."""

        return self.__payload.get([ns.PARAM], self.__payload.get_name())


def validate_parameter_list(params: List[Param]):
    """
    Check that all the items in the list are Param instances.

    :raises: ValueError

    """

    if not params:
        return

    for param in params:
        if not isinstance(param, Param):
            raise ValueError(f'The parameter is not an instance of Param: {param.__class__}')
