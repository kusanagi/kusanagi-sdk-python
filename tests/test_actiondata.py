# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_actiondata_entity():
    from kusanagi.sdk import ActionData

    data = [{'bar': 'baz'}]
    action_data = ActionData('foo', data)
    assert action_data.get_name() == 'foo'
    assert action_data.get_data() == data
    assert not action_data.is_collection()


def test_actiondata_collection():
    from kusanagi.sdk import ActionData

    data = [[{'bar': 'baz'}]]
    action_data = ActionData('foo', data)
    assert action_data.get_name() == 'foo'
    assert action_data.get_data() == data
    assert action_data.is_collection()
