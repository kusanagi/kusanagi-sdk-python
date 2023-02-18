# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2023 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_payload_reply_defaults():
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload()
    assert reply.get_return_value() is None
    assert reply.get_transport() is None


def test_lib_payload_reply():
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload
    from kusanagi.sdk.lib.payload.transport import TransportPayload

    reply = ReplyPayload()
    reply.set([ns.TRANSPORT], {'a': 'b'})
    reply.set([ns.RETURN], 42)
    assert reply.get_return_value() == 42
    assert isinstance(reply.get_transport(), TransportPayload)


def test_lib_payload_reply_request(command):
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload.new_request_reply(command)
    assert isinstance(reply, ReplyPayload)
    assert reply.exists([ns.COMMAND_REPLY, ns.NAME], prefix=False)
    assert len(reply.get([ns.COMMAND_REPLY], {}, prefix=False)) == 2
    assert len(reply.get([ns.COMMAND_REPLY, ns.RESULT], {}, prefix=False)) == 3
    assert reply.exists([ns.ATTRIBUTES])
    assert len(reply.get([ns.CALL], {})) == 4
    assert reply.exists([ns.CALL, ns.SERVICE])
    assert reply.exists([ns.CALL, ns.VERSION])
    assert reply.exists([ns.CALL, ns.ACTION])
    assert reply.exists([ns.CALL, ns.PARAMS])
    assert len(reply.get([ns.RESPONSE], {})) == 4
    assert reply.exists([ns.RESPONSE, ns.VERSION])
    assert reply.exists([ns.RESPONSE, ns.STATUS])
    assert reply.exists([ns.RESPONSE, ns.HEADERS])
    assert reply.exists([ns.RESPONSE, ns.BODY])

    # A response can be setted into the request reply when the middleware
    # nees to stop the workflow and return a response without calling the
    # service or other middlewares in the queue.
    assert reply.get([ns.RESPONSE, ns.VERSION]) == ReplyPayload.HTTP_VERSION
    assert reply.get([ns.RESPONSE, ns.STATUS]) == ReplyPayload.HTTP_STATUS_OK
    assert reply.get([ns.RESPONSE, ns.HEADERS]) == {'Content-Type': ['text/plain']}
    assert reply.get([ns.RESPONSE, ns.BODY]) == b''
    assert isinstance(reply.set_response(500, 'Error'), ReplyPayload)
    assert reply.get([ns.RESPONSE, ns.VERSION]) == ReplyPayload.HTTP_VERSION
    assert reply.get([ns.RESPONSE, ns.STATUS]) == '500 Error'
    assert reply.get([ns.RESPONSE, ns.HEADERS]) == {}
    assert reply.get([ns.RESPONSE, ns.BODY]) == b''

    # When the payload is used as a request payload it must not contain a response
    assert reply.exists([ns.RESPONSE])
    assert isinstance(reply.for_request(), ReplyPayload)
    assert not reply.exists([ns.RESPONSE])


def test_lib_payload_reply_response(command):
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload.new_response_reply(command)
    assert isinstance(reply, ReplyPayload)
    assert len(reply.get([ns.COMMAND_REPLY], {}, prefix=False)) == 2
    assert reply.exists([ns.COMMAND_REPLY, ns.NAME], prefix=False)
    assert len(reply.get([ns.COMMAND_REPLY, ns.RESULT], {}, prefix=False)) == 2
    assert reply.exists([ns.ATTRIBUTES])
    assert reply.exists([ns.RESPONSE])

    # When the payload is used as a response payload it must not contain the call info
    assert reply.set([ns.CALL], {})
    assert reply.exists([ns.CALL])
    assert isinstance(reply.for_response(), ReplyPayload)
    assert not reply.exists([ns.CALL])


def test_lib_payload_reply_action(command):
    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload.new_action_reply(command)
    assert isinstance(reply, ReplyPayload)
    assert len(reply) == 1
    assert len(reply.get([ns.COMMAND_REPLY], {}, prefix=False)) == 2
    assert reply.exists([ns.COMMAND_REPLY, ns.NAME], prefix=False)
    assert len(reply.get([ns.COMMAND_REPLY, ns.RESULT], {}, prefix=False)) == 1
    assert reply.exists([ns.TRANSPORT])
