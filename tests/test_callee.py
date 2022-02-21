# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_callee_defaults():
    from kusanagi.sdk import ActionSchema
    from kusanagi.sdk import Callee
    from kusanagi.sdk.lib.payload import Payload

    callee = Callee(Payload())
    assert callee.get_duration() == 0
    assert not callee.is_remote()
    assert callee.get_address() == ''
    assert callee.get_timeout() == ActionSchema.DEFAULT_EXECUTION_TIMEOUT
    assert callee.get_name() == ''
    assert callee.get_version() == ''
    assert callee.get_action() == ''
    assert callee.get_params() == []


def test_callee():
    from kusanagi.sdk import Callee
    from kusanagi.sdk import Param
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload import Payload

    payload = {
        ns.DURATION: 10,
        ns.GATEWAY: 'ktp://1.2.3.4:77',
        ns.TIMEOUT: 10000,
        ns.NAME: 'foo',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'bar',
        ns.PARAMS: [{
            ns.NAME: 'foo',
            ns.VALUE: 'bar',
        }],
    }
    callee = Callee(Payload(payload))
    assert callee.get_duration() == payload[ns.DURATION]
    assert callee.is_remote()
    assert callee.get_address() == payload[ns.GATEWAY]
    assert callee.get_timeout() == payload[ns.TIMEOUT]
    assert callee.get_name() == payload[ns.NAME]
    assert callee.get_version() == payload[ns.VERSION]
    assert callee.get_action() == payload[ns.ACTION]
    params = callee.get_params()
    assert len(params) == 1
    assert isinstance(params[0], Param)
