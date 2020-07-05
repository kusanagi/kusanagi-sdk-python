# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_link():
    from kusanagi.sdk import Link

    link = Link('1.2.3.4:77', 'foo', 'bar', '/test')
    assert link.get_address() == '1.2.3.4:77'
    assert link.get_name() == 'foo'
    assert link.get_link() == 'bar'
    assert link.get_uri() == '/test'
