# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_servicedata():
    from kusanagi.sdk import ActionData
    from kusanagi.sdk import ServiceData

    service_data = ServiceData('1.2.3.4:77', 'foo', '1.0.0', {'bar': [{'value': 77}]})
    assert service_data.get_address() == '1.2.3.4:77'
    assert service_data.get_name() == 'foo'
    assert service_data.get_version() == '1.0.0'
    actions = service_data.get_actions()
    assert isinstance(actions, list)
    assert len(actions) == 1
    action_data = actions[0]
    assert isinstance(action_data, ActionData)
    assert action_data.get_name() == 'bar'
    assert action_data.get_data() == [{'value': 77}]
