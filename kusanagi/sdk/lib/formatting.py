# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import time
from datetime import date
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = f'{DATE_FORMAT}T{TIME_FORMAT}.%f+00:00'


def str_to_datetime(value: str) -> datetime:
    """
    Convert a datetime string to a datetime object.

    :param value: A datetime string value.

    """

    return datetime.strptime(value, DATETIME_FORMAT)


def datetime_to_str(value: datetime) -> str:
    """
    Convert a datetime object to string.

    :param value: A datetime to convert.

    """

    return value.strftime(DATETIME_FORMAT)


def str_to_date(value: str) -> date:
    """
    Convert a date string to a date object.

    :param value: A date string to convert.

    """

    return datetime.strptime(value, DATE_FORMAT).date()


def date_to_str(value: date) -> str:
    """
    Convert a date object to string.

    :param value: A date to convert.

    """

    return value.strftime(DATE_FORMAT)


def time_to_str(value: time.struct_time) -> str:
    """
    Convert a time struct object to string.

    :param value: A time to convert.

    """

    return time.strftime(TIME_FORMAT, value)
