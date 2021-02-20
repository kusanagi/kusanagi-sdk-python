# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_caller():
    from kusanagi.sdk import Callee
    from kusanagi.sdk import Caller

    caller = Caller('foo', '1.0.0', 'bar', {})
    assert caller.get_name() == 'foo'
    assert caller.get_version() == '1.0.0'
    assert caller.get_action() == 'bar'
    assert isinstance(caller.get_callee(), Callee)
