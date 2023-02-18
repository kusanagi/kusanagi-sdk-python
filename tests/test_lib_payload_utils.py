# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_file_to_payload():
    from kusanagi.sdk import File
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.utils import file_to_payload

    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='file.json',
        size=600,
        token='secret',
    )
    payload = file_to_payload(file)
    assert payload is not None
    assert payload.get([ns.NAME]) == file.get_name()
    assert payload.get([ns.PATH]) == file.get_path()
    assert payload.get([ns.MIME]) == file.get_mime()
    assert payload.get([ns.FILENAME]) == file.get_filename()
    assert payload.get([ns.SIZE]) == file.get_size()
    assert payload.get([ns.TOKEN]) == file.get_token()


def test_payload_to_file():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.utils import payload_to_file

    payload = {
        ns.NAME: 'foo',
        ns.PATH: 'http://127.0.0.1:8080/ANBDKAD23142421',
        ns.MIME: 'application/json',
        ns.FILENAME: 'file.json',
        ns.SIZE: 600,
        ns.TOKEN: 'secret',
    }
    file = payload_to_file(payload)
    assert file is not None
    assert file.get_name() == payload[ns.NAME]
    assert file.get_path() == payload[ns.PATH]
    assert file.get_mime() == payload[ns.MIME]
    assert file.get_filename() == payload[ns.FILENAME]
    assert file.get_size() == payload[ns.SIZE]
    assert file.get_token() == payload[ns.TOKEN]


def test_merge_dictionary():
    from kusanagi.sdk.lib.payload.utils import merge_dictionary

    src = {
        '1': 1,
        '2': [1],
        '3': {'a': 1},
        '4': {'a': {'b': 2}},
        '5': {'a': {'b': [2]}},
        '6': {},
        '7': [],
    }
    dst = {
        '2': [3],
        '3': {'c': 3},
        '4': {'a': {'c': 3}},
        '5': {'a': {'b': [3]}},
        '8': 3,
    }
    dst = merge_dictionary(src, dst)
    assert dst == {
        '1': 1,
        '2': [3, 1],
        '3': {'a': 1, 'c': 3},
        '4': {'a': {'b': 2, 'c': 3}},
        '5': {'a': {'b': [3, 2]}},
        '6': {},
        '7': [],
        '8': 3,
    }
