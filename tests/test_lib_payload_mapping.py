# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_lib_payload_mapping_defaults():
    from kusanagi.sdk.lib.payload.mapping import MappingPayload

    payload = MappingPayload()
    assert list(payload.get_services()) == []

    with pytest.raises(LookupError):
        payload.get_service_schema_payload('foo', '2.0.0')


def test_lib_payload_mapping():
    from kusanagi.sdk.lib.payload.mapping import MappingPayload

    payload = MappingPayload({
        'foo': {
            '1.1.0': {'value': 1},
            '1.2.0': {'value': 2},
        },
        'bar': {
            '1.1.0': {'value': 3},
        },
    })

    services = list(payload.get_services())
    assert len(services) == 3
    assert {'name': 'foo', 'version': '1.1.0'} in services
    assert {'name': 'foo', 'version': '1.2.0'} in services
    assert {'name': 'bar', 'version': '1.1.0'} in services

    schema = payload.get_service_schema_payload('foo', '1.1.0')
    assert schema == payload['foo']['1.1.0']

    # This must resolve to the higher compatible version
    schema = payload.get_service_schema_payload('foo', '1.*.0')
    assert schema == payload['foo']['1.2.0']
