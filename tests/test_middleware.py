# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_middleware_response():
    from kusanagi.sdk import Middleware

    def callback(request):
        pass

    middleware = Middleware()
    assert 'request' not in middleware._callbacks
    assert middleware.request(callback) == middleware
    assert middleware._callbacks.get('request') == callback


def test_middleware_request():
    from kusanagi.sdk import Middleware

    def callback(request):
        pass

    middleware = Middleware()
    assert 'response' not in middleware._callbacks
    assert middleware.response(callback) == middleware
    assert middleware._callbacks.get('response') == callback
