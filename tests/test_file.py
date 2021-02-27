# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import os
import sys
from unittest import mock

import pytest


def test_file_empty_read():
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError

    file = File('')
    with pytest.raises(KusanagiError):
        file.read()


def test_file_local(DATA_DIR):
    from kusanagi.sdk import File

    path = os.path.join(DATA_DIR, 'file.txt')
    file = File('foo', path=f'file://{path}', mime='text/plain', filename='file.txt', size=42)
    assert file.is_local()
    assert file.get_name() == 'foo'
    assert file.get_path() == f'file://{path}'
    assert file.get_mime() == 'text/plain'
    assert file.get_filename() == 'file.txt'
    assert file.get_size() == 42
    assert file.get_token() == ''


def test_file_local_relative_path(DATA_DIR):
    from kusanagi.sdk import File

    path = os.path.join(DATA_DIR, 'file.txt')
    file = File('foo', path=path, mime='text/plain')
    assert file.is_local()
    # The path is prefixed with "file://"
    assert file.get_path() == f'file://{path}'


def test_file_local_invalid(DATA_DIR):
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError

    path = os.path.join(DATA_DIR, 'invalid.txt')
    with pytest.raises(KusanagiError):
        File('foo', path=f'file://{path}')


def test_file_local_no_mime(DATA_DIR):
    from kusanagi.sdk import File

    filename = 'file.txt'
    path = os.path.join(DATA_DIR, filename)
    file = File('foo', path=f'file://{path}', size=42)
    assert file.get_name() == 'foo'
    assert file.get_path() == f'file://{path}'
    assert file.get_mime() == 'text/plain'
    assert file.get_filename() == filename
    assert file.get_size() == 42
    assert file.get_token() == ''


def test_file_local_no_filename(DATA_DIR):
    from kusanagi.sdk import File

    filename = 'file.txt'
    path = os.path.join(DATA_DIR, filename)
    file = File('foo', path=f'file://{path}', mime='text/plain', size=42)
    assert file.get_name() == 'foo'
    assert file.get_path() == f'file://{path}'
    assert file.get_mime() == 'text/plain'
    assert file.get_filename() == filename
    assert file.get_size() == 42
    assert file.get_token() == ''


def test_file_local_no_size(DATA_DIR):
    from kusanagi.sdk import File

    path = os.path.join(DATA_DIR, 'file.txt')
    file = File('foo', path=f'file://{path}', mime='text/plain', filename='file.txt')
    assert file.get_name() == 'foo'
    assert file.get_path() == f'file://{path}'
    assert file.get_mime() == 'text/plain'
    assert file.get_filename() == 'file.txt'
    assert file.get_size() == 4  # The size is calculated when is not given
    assert file.get_token() == ''


def test_file_local_with_token():
    from kusanagi.sdk import File

    # Local file doesn't allow tokens
    with pytest.raises(ValueError):
        File('foo', path='file://test.json', token='XYZ')


def test_file_local_read(DATA_DIR):
    from kusanagi.sdk import File

    path = os.path.join(DATA_DIR, 'file.txt')
    file = File('foo', path=f'file://{path}', mime='text/plain', size=42)
    assert file.read() == b'foo\n'


def test_file_local_read_fail(DATA_DIR):
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError

    # Creation check that the file exists
    with pytest.raises(KusanagiError):
        file = File('foo', path='file://invalid.txt', mime='text/plain', size=42)

    # Create a valid file and the change the file name to an invalid one
    with mock.patch('kusanagi.sdk.file.open', create=True) as mocked_open:
        mocked_open.side_effect = Exception

        path = os.path.join(DATA_DIR, 'file.txt')
        file = File('foo', path=f'file://{path}', mime='text/plain', size=42)
        with pytest.raises(KusanagiError):
            file.read()


def test_file_remote():
    from kusanagi.sdk import File

    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='ANBDKAD23142421',
        size=42,
        token='XYZ',
    )
    assert not file.is_local()
    assert file.get_name() == 'foo'
    assert file.get_path() == 'http://127.0.0.1:8080/ANBDKAD23142421'
    assert file.get_mime() == 'application/json'
    assert file.get_filename() == 'ANBDKAD23142421'
    assert file.get_size() == 42
    assert file.get_token() == 'XYZ'


def test_file_remote_no_mime():
    from kusanagi.sdk import File

    with pytest.raises(ValueError):
        File('foo', path='http://127.0.0.1:8080/ANBDKAD23142421')


def test_file_remote_no_filename():
    from kusanagi.sdk import File

    with pytest.raises(ValueError):
        File('foo', path='http://127.0.0.1:8080/ANBDKAD23142421', mime='application/json')


def test_file_remote_invalid_size():
    from kusanagi.sdk import File

    with pytest.raises(ValueError):
        File(
            'foo',
            path='http://127.0.0.1:8080/ANBDKAD23142421',
            mime='application/json',
            filename='ANBDKAD23142421',
            size=-1,
        )


def test_file_remote_no_token():
    from kusanagi.sdk import File

    with pytest.raises(ValueError):
        File(
            'foo',
            path='http://127.0.0.1:8080/ANBDKAD23142421',
            mime='application/json',
            filename='ANBDKAD23142421',
            size=42,
        )


def test_file_remote_read(DATA_DIR, mocker):
    from kusanagi.sdk import File

    # Mock a request reader
    request = mocker.MagicMock()
    request.read.return_value = b'foo'

    # Mock the "urllib.request.urlopen"
    reader = mocker.MagicMock()
    reader.__enter__.return_value = request
    reader.__exit__.return_value = False
    mocker.patch('urllib.request.urlopen', return_value=reader)

    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='ANBDKAD23142421',
        size=42,
        token='XYZ',
    )
    assert file.read() == b'foo'


def test_file_remote_read_fail(DATA_DIR, mocker):
    from kusanagi.sdk import File
    from kusanagi.sdk import KusanagiError

    # Mock a request reader
    request = mocker.MagicMock()
    request.read.side_effect = Exception

    # Mock the "urllib.request.urlopen"
    reader = mocker.MagicMock()
    reader.__enter__.return_value = request
    reader.__exit__.return_value = False
    mocker.patch('urllib.request.urlopen', return_value=reader)

    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='ANBDKAD23142421',
        size=42,
        token='XYZ',
    )
    with pytest.raises(KusanagiError):
        assert file.read() == b'foo'


def test_file_parameter_exist(DATA_DIR):
    from kusanagi.sdk import File

    # Empty files doesn't exist as parameters
    file = File('')
    assert not file.exists()

    # Local files doesn't exist as parameters until the are uses in a call
    path = os.path.join(DATA_DIR, 'file.txt')
    file = File('foo', path=f'file://{path}', mime='text/plain', filename='file.txt')
    assert file.is_local()
    assert not file.exists()

    # Remote HTTP files exist because they were send in a request or a call
    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='ANBDKAD23142421',
        size=42,
        token='XYZ',
    )
    assert not file.is_local()
    assert file.exists()


def test_file_copy():
    from kusanagi.sdk import File

    file = File(
        'foo',
        path='http://127.0.0.1:8080/ANBDKAD23142421',
        mime='application/json',
        filename='ANBDKAD23142421',
        size=42,
        token='XYZ',
    )

    new_file = file.copy_with_name('bar')
    assert isinstance(new_file, File)
    assert new_file != file
    assert new_file.get_name() == 'bar'
    assert new_file.get_path() == file.get_path()
    assert new_file.get_size() == file.get_size()
    assert new_file.get_mime() == file.get_mime()
    assert new_file.get_token() == file.get_token()

    new_file = file.copy_with_mime('text/plain')
    assert isinstance(new_file, File)
    assert new_file != file
    assert new_file.get_mime() == 'text/plain'
    assert new_file.get_name() == file.get_name()
    assert new_file.get_path() == file.get_path()
    assert new_file.get_size() == file.get_size()
    assert new_file.get_token() == file.get_token()


def test_file_schema_defaults():
    from kusanagi.sdk import FileSchema
    from kusanagi.sdk import HttpFileSchema
    from kusanagi.sdk.lib.payload.file import FileSchemaPayload

    schema = FileSchema(FileSchemaPayload('foo'))
    assert schema.get_name() == 'foo'
    assert schema.get_mime() == 'text/plain'
    assert not schema.is_required()
    assert schema.get_max() == sys.maxsize
    assert not schema.is_exclusive_max()
    assert schema.get_min() == 0
    assert not schema.is_exclusive_min()

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpFileSchema)
    assert http_schema.is_accessible()
    assert http_schema.get_param() == schema.get_name()


def test_file_schema():
    from kusanagi.sdk import FileSchema
    from kusanagi.sdk import HttpFileSchema
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.file import FileSchemaPayload

    payload = {
        ns.MIME: 'application/json',
        ns.REQUIRED: True,
        ns.MAX: 100444,
        ns.EXCLUSIVE_MAX: True,
        ns.MIN: 100,
        ns.EXCLUSIVE_MIN: True,
        ns.HTTP: {
            ns.GATEWAY: False,
            ns.PARAM: 'upload',
        }
    }

    schema = FileSchema(FileSchemaPayload('foo', payload))
    assert schema.get_name() == 'foo'
    assert schema.get_mime() == payload[ns.MIME]
    assert schema.is_required()
    assert schema.get_max() == payload[ns.MAX]
    assert schema.is_exclusive_max()
    assert schema.get_min() == payload[ns.MIN]
    assert schema.is_exclusive_min()

    http_schema = schema.get_http_schema()
    assert isinstance(http_schema, HttpFileSchema)
    assert not http_schema.is_accessible()
    assert http_schema.get_param() == payload[ns.HTTP][ns.PARAM]


def test_validate_file_list():
    from kusanagi.sdk import File
    from kusanagi.sdk.file import validate_file_list

    assert validate_file_list([]) is None
    assert validate_file_list([File('a'), File('b')]) is None

    with pytest.raises(ValueError):
        assert validate_file_list([File('a'), 'boom!']) is None
