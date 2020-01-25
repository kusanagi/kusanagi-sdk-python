# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2019 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from ..errors import KusanagiError
from ..payload import get_path
from ..payload import Payload

EMPTY = object()

# Supported parameter types
TYPE_NULL = 'null'
TYPE_BOOLEAN = 'boolean'
TYPE_INTEGER = 'integer'
TYPE_FLOAT = 'float'
TYPE_ARRAY = 'array'
TYPE_OBJECT = 'object'
TYPE_STRING = 'string'
TYPE_BINARY = 'binary'

# Parameter type names to python types
TYPE_CLASSES = {
    TYPE_BOOLEAN: bool,
    TYPE_INTEGER: int,
    TYPE_FLOAT: float,
    TYPE_ARRAY: list,
    TYPE_OBJECT: dict,
    TYPE_STRING: str,
    TYPE_BINARY: bytes,
    }


class InvalidFallback(KusanagiError):
    pass


def payload_to_param(payload):
    """Convert a param payload to a Param object.

    :param payload: Parameter payload.
    :type payload: Payload

    :rtype: Param

    """

    return Param(
        get_path(payload, 'name'),
        value=get_path(payload, 'value'),
        type=get_path(payload, 'type'),
        exists=True,
        )


def param_to_payload(param):
    """Convert a Param object to a param payload.

    :param param: Parameter object.
    :type param: Param

    :rtype: Payload

    """

    return Payload().set_many({
        'name': param.get_name(),
        'value': param.get_value(),
        'type': param.get_type(),
        })


class Param(object):
    """Parameter class for API.

    A Param object represents a parameter received for an action in a call
    to a Service component.

    """

    def __init__(self, name, value='', type=TYPE_STRING, exists=True):
        """
        Constructor.

        :param name: Name of the parameter.
        :param value: Optional value for the parameter.
        :param type: Optional type for the parameter value.
        :param exists: Optional flag to know if the parameter exists in the service call.

        :raises: TypeError

        """

        # Invalid parameter types are treated as string parameters
        if type not in TYPE_CLASSES:
            type = TYPE_STRING

        # Check that the value respects the parameter type
        if type == TYPE_NULL and value is not None:
            raise TypeError('Value must be null')
        else:
            type_cls = TYPE_CLASSES[type]
            if not isinstance(type_cls, value):
                raise TypeError(f'Value must be {type}')

        self.__name = name
        self.__value = value
        self.__type = type
        self.__exists = exists

    @classmethod
    def resolve_type(cls, value):
        """Converts native types to schema types.

        :param value: The value to analyze.
        :type value: mixed

        :rtype: str

        """

        if value is None:
            return TYPE_NULL

        value_class = value.__class__

        # Resolve non standard python types
        if value_class in (tuple, set):
            return TYPE_ARRAY

        # Resolve standard mapped python types
        for type_name, cls in TYPE_CLASSES.items():
            if value_class == cls:
                return type_name

        return TYPE_OBJECT

    def get_name(self):
        """Get aprameter name.

        :rtype: str

        """

        return self.__name

    def get_type(self):
        """Get parameter data type.

        :rtype: str

        """

        return self.__type

    def get_value(self, fallback=None):
        """Get parameter value.

        Value is returned using the parameter data type for casting.

        :param fallback: The optional fallback value, which must be null or conform to the data type. If a callable is 
        provided it will be evaluated if the fallback is to be returned.
        :type fallback: mixed
        :returns: The parameter value.
        :rtype: object
        :raises: InvalidFallback

        """

        if not self.__exists:
            if self.__type == TYPE_NULL:
                return

            if fallback is not None:
                if callable(fallback):
                    fallback = fallback()

                name = self.__name

                if not isinstance(fallback, TYPE_CLASSES[self.__type]):
                    raise InvalidFallback(f'Invalid data type for fallback of parameter: {name}')

                return fallback

        return self.__value

    def exists(self):
        """Check if parameter exists.

        :rtype: bool

        """

        return self.__exists

    def copy_with_name(self, name):
        return self.__class__(name, value=self.__value, type=self.__type)

    def copy_with_value(self, value):
        return self.__class__(self.__name, value=value, type=self.__type)

    def copy_with_type(self, type):
        return self.__class__(self.__name, value=self.__value, type=type)
