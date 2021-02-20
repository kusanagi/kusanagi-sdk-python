# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_state_invalid_multipart(logs, input_):
    from kusanagi.sdk.lib.state import State

    assert State.create(input_, []) is None
    assert logs.getvalue() != ''


def test_lib_state(input_, stream):
    from kusanagi.sdk.lib.logging import RequestLogger
    from kusanagi.sdk.lib.state import State

    request_id = stream[0].decode('utf8')

    state = State.create(input_, stream)
    assert state is not None
    assert state.id == request_id
    assert state.action == stream[1].decode('utf8')
    assert state.schemas == stream[2]
    assert state.payload == stream[3]
    assert state.values == input_
    assert isinstance(state.logger, RequestLogger)
    assert state.logger.rid == request_id
    assert state.get_component_title() == '"{}" ({})'.format(
        state.values.get_name(),
        state.values.get_version(),
    )
