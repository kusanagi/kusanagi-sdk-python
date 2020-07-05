# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import datetime
import decimal
import json
from typing import Any

from .formatting import date_to_str
from .formatting import datetime_to_str


class Encoder(json.JSONEncoder):
    """Class to handle JSON encoding for custom types."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return datetime_to_str(obj)
        elif isinstance(obj, datetime.date):
            return date_to_str(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf8')

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def loads(value: str) -> Any:
    """
    Convert a JSON string to Python.

    :param value: A JSON string to deserialize.

    """

    return json.loads(value)


def dumps(obj: Any, prettify: bool = False) -> bytes:
    """
    Convert a python type to a JSON string.

    The result value is encoded as UTF-8.

    :param obj: The python type to serialize.
    :param prettify: Optional flag to enable formatting of the result.

    """

    if not prettify:
        value = json.dumps(obj, separators=(',', ':'), cls=Encoder)
    else:
        value = json.dumps(obj, indent=2, cls=Encoder)

    return value.encode('utf-8')
