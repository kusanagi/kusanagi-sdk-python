# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import copy

from ...file import File
from ...param import Param
from . import Payload
from . import ns


def payload_to_param(p: dict) -> Param:
    """
    Convert a payload to an SDK parameter.

    :param p: The parameter payload.

    """

    return Param(
        p.get(ns.NAME),
        value=p.get(ns.VALUE),
        type=p.get(ns.TYPE),
        exists=True,
    )


def param_to_payload(p: Param) -> Payload:
    """
    Convert a parameter object to a payload.

    :param p: The parameter object.

    """

    return Payload({
        ns.NAME: p.get_name(),
        ns.VALUE: p.get_value(),
        ns.TYPE: p.get_type(),
    })


def file_to_payload(f: File) -> Payload:
    """
    Convert a file to a payload.

    :param f: The file object.

    """

    p = Payload({
        ns.NAME: f.get_name(),
        ns.PATH: f.get_path(),
        ns.MIME: f.get_mime(),
        ns.FILENAME: f.get_filename(),
        ns.SIZE: f.get_size(),
    })

    if f.get_path() and not f.is_local():
        p[ns.TOKEN] = f.get_token()

    return p


def payload_to_file(p: dict) -> File:
    """
    Convert payload to a file.

    :param p: The file payload.

    """

    return File(
        p.get(ns.NAME),
        p.get(ns.PATH),
        mime=p.get(ns.MIME),
        filename=p.get(ns.FILENAME),
        size=p.get(ns.SIZE),
        token=p.get(ns.TOKEN),
    )


def merge_dictionary(src: dict, dest: dict) -> dict:
    """
    Merge two dictionaries.

    :param src: A dictionary with the values to merge.
    :param dest: A dictionary where to merge the values.

    """

    for name, value in src.items():
        if name not in dest:
            # When field is not available in destination add the value from the source
            if isinstance(value, dict):
                # A new dictionary is created to avoid keeping references
                dest[name] = copy.deepcopy(value)
            elif isinstance(value, list):
                # A new list is created to avoid keeping references
                dest[name] = copy.deepcopy(value)
            else:
                dest[name] = value
        elif isinstance(value, dict):
            # When field exists in destination and is dict merge the source value
            merge_dictionary(value, dest[name])
        elif isinstance(value, list) and isinstance(dest[name], list):
            # When both values are a list merge them
            dest[name].extend(copy.deepcopy(value))

    return dest
