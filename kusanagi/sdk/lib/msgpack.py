# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import datetime
import decimal
import time
from typing import Any
from typing import List

import msgpack

from .formatting import date_to_str
from .formatting import datetime_to_str
from .formatting import str_to_date
from .formatting import str_to_datetime
from .formatting import time_to_str


def _encode(obj: Any) -> List:
    """
    Handle packing for custom types.

    Custom types are serialized as list, where first item is the string "type",
    the second is the data type name and the third is the value represented as
    a basic type.

    :raises: TypeError

    """

    if isinstance(obj, decimal.Decimal):
        # Decimal is represented as a tuple of strings
        return ['type', 'decimal', str(obj).split('.')]
    elif isinstance(obj, datetime.datetime):
        return ['type', 'datetime', datetime_to_str(obj)]
    elif isinstance(obj, datetime.date):
        return ['type', 'date', date_to_str(obj)]
    elif isinstance(obj, time.struct_time):
        return ['type', 'time', time_to_str(obj)]

    raise TypeError(f'{repr(obj)} is not serializable')


def _decode(data: List) -> Any:
    """
    Handle unpacking for custom types.

    None is returned when the type is not recognized.

    """

    if len(data) == 3 and data[0] == 'type':
        data_type = data[1]
        try:
            if data_type == 'decimal':
                # Decimal is represented as a tuple of strings
                return decimal.Decimal('.'.join(data[2]))
            elif data_type == 'datetime':
                return str_to_datetime(data[2])
            elif data_type == 'date':
                return str_to_date(data[2])
            elif data_type == 'time':
                # Use time as a string "HH:MM:SS"
                return data[2]
        except Exception:
            # Don't fail when there are inconsistent data values.
            # Invalid values will be null.
            return

    return data


def pack(value: Any) -> bytes:
    """
    Pack python data to a binary stream.

    :param value: A python object to serialize.

    """

    return msgpack.packb(value, default=_encode, use_bin_type=True)


def unpack(value: bytes) -> Any:
    """
    Pack python data to a binary stream.

    :param value: The binary stream to deserialize.

    """

    return msgpack.unpackb(value, list_hook=_decode, raw=False)
