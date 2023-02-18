# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import os


def test_lib_payload_command_defaults():
    from kusanagi.sdk.lib.payload.command import CommandPayload

    payload = CommandPayload()
    assert payload.get_name() == ''
    assert payload.get_attributes() == {}
    assert payload.get_service_call_data() == {}
    assert payload.get_transport_data() == {}
    assert payload.get_response_data() == {}
    assert payload.get_request_id() == ''


def test_lib_payload_command():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    payload = CommandPayload.new('foo', 'service', {'bar': 'baz'})
    assert isinstance(payload, CommandPayload)
    assert payload.get_name() == 'foo'
    assert payload.get([ns.META, ns.SCOPE], prefix=False) == 'service'
    assert payload.get([ns.COMMAND, ns.ARGUMENTS], prefix=False) == {'bar': 'baz'}
    assert len(payload) == 2
    assert len(payload.get([ns.COMMAND], prefix=False)) == 2
    assert len(payload.get([ns.META], prefix=False)) == 1

    assert not payload.exists([ns.ATTRIBUTES])
    payload.set([ns.ATTRIBUTES], {'a': 1})
    assert payload.get_attributes() == {'a': 1}

    payload.set([ns.CALL], {'c': 2})
    assert payload.get_service_call_data() == {'c': 2}

    payload.set([ns.TRANSPORT], {'b': 3})
    assert payload.get_transport_data() == {'b': 3}

    payload.set([ns.RESPONSE], {'c': 4})
    assert payload.get_response_data() == {'c': 4}

    # The request ID in the meta has more precedence than the one in the transport
    payload.set([ns.TRANSPORT, ns.META, ns.ID], '25759c6c-8531-40d2-a415-4ff9246307c5')
    assert payload.get_request_id() == '25759c6c-8531-40d2-a415-4ff9246307c5'
    payload.set([ns.META, ns.ID], 'e60d3293-5c2a-4d19-9964-24ab122b04a6')
    assert payload.get_request_id() == 'e60d3293-5c2a-4d19-9964-24ab122b04a6'


def test_lib_payload_command_runtime_call(DATA_DIR):
    from kusanagi.sdk import File
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    params = [Param('foop')]
    path = os.path.join(DATA_DIR, 'file.txt')
    files = [File('foof', path)]
    payload = CommandPayload.new_runtime_call('foo', 'bar', '1.2.3', 'baz', params, files, {'value': 1})
    assert isinstance(payload, CommandPayload)
    assert payload.get_name() == 'runtime-call'
    assert payload.get([ns.META, ns.SCOPE], prefix=False) == 'service'
    assert payload.get([ns.ACTION]) == 'foo'
    assert payload.get([ns.CALLEE]) == ['bar', '1.2.3', 'baz']
    assert payload.get([ns.TRANSPORT]) == {'value': 1}
    assert len(payload.get([ns.PARAMS])) == 1
    param = payload.get([ns.PARAMS])[0]
    assert param[ns.NAME] == 'foop'
    assert len(payload.get([ns.FILES])) == 1
    file = payload.get([ns.FILES])[0]
    assert file[ns.NAME] == 'foof'
    assert file[ns.PATH] == f'file://{path}'
