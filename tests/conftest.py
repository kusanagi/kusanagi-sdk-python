# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import io
import os
import logging

import pytest


@pytest.fixture(scope='session')
def DATA_DIR(request) -> str:
    """Path to the tests data directory."""

    return os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope='session')
def schemas():
    """Service mapping schemas."""

    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.mapping import MappingPayload

    return MappingPayload({
        'foo': {
            '1.0.0': {
                ns.ADDRESS: '1.2.3.4:77',
                ns.HTTP: {
                    ns.PATH: '/test',
                },
                ns.ACTIONS: {
                    'bar': {},
                },
            },
        },
    })


@pytest.fixture(scope='function')
def input_(DATA_DIR):
    """CLI input values."""

    from kusanagi.sdk.lib.cli import Input

    return Input(
        os.path.join(DATA_DIR, 'test.py'),
        component='service',
        name='foo',
        version='1.0.0',
        framework_version='3.0.0',
        socket='@kusanagi-1.2.3.4-77',
        timeout=10000,
        debug=True,
        var={'foo': 'bar', 'bar': 'baz'},
        log_level='debug',
        tcp=None,
    )


@pytest.fixture(scope='session')
def stream():
    """ZMQ request stream."""

    from kusanagi.sdk.lib.msgpack import pack

    return [b'72642c64-a37e-45cc-8f1e-7225b0b1b8e0', b'bar', b'', pack({})]


@pytest.fixture(scope='function')
def state(input_, stream):
    """Framework request state."""

    from kusanagi.sdk.lib.state import State

    return State(input_, stream)


@pytest.fixture(scope='function')
def logs(request, mocker):
    """Enable logging output support in a test."""

    from kusanagi.sdk.lib.logging import setup_kusanagi_logging

    output = io.StringIO()

    def cleanup():
        # Remove root handlers to release sys.stdout
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)

        # Cleanup kusanagi logger handlers too
        logging.getLogger('kusanagi').handlers = []
        # Close the output stream
        output.close()

    request.addfinalizer(cleanup)
    mocker.patch('kusanagi.sdk.lib.logging.get_output_buffer', return_value=output)
    setup_kusanagi_logging('component', 'name', 'version', 'framework-version', logging.DEBUG)
    return output


@pytest.fixture(scope='function')
def command():
    """Get a command payload."""

    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.command import CommandPayload

    command = CommandPayload()
    command.set([ns.META], {
        ns.ID: '25759c6c-8531-40d2-a415-4ff9246307c5',
        ns.DATETIME: '2017-01-27T20:12:08.952811+00:00',
        ns.PROTOCOL: 'http',
        ns.GATEWAY: ["1.2.3.4:1234", "http://1.2.3.4:77"],
        ns.CLIENT: '7.7.7.7:6666',
        ns.ATTRIBUTES: {'foo': 'bar'},
    })
    command.set([ns.REQUEST], {
        ns.HEADERS: {'fooh': ['barh', 'bazh']},
        ns.FILES: [{
            ns.NAME: 'foof',
        }],
        ns.METHOD: 'PUT',
        ns.URL: 'http://6.6.6.6:7777/test',
        ns.QUERY: {'fooq': ['barq', 'bazq']},
        ns.POST_DATA: {'foop': ['barp', 'bazp']},
        ns.VERSION: '2.0',
        ns.BODY: b'contents',
    })
    return command


@pytest.fixture(scope='function')
def reply():
    """Get a reply payload."""

    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.reply import ReplyPayload

    reply = ReplyPayload()
    reply.set([ns.CALL], {
        ns.SERVICE: 'foo',
        ns.VERSION: '1.0.0',
        ns.ACTION: 'bar',
    })
    return reply


@pytest.fixture(scope='function')
def action_reply(reply):
    """Get a reply payload for an action."""

    from kusanagi.sdk.lib.payload import ns

    reply.set([ns.TRANSPORT, ns.META, ns.ORIGIN], ['foo', '1.0.0', 'bar'])
    return reply


@pytest.fixture(scope='function')
def response_reply(reply):
    """Get a reply payload for a response."""

    from kusanagi.sdk.lib.payload import ns

    reply.set([ns.RESPONSE], {
        ns.HEADERS: {'fooh': ['barh', 'bazh']},
        ns.VERSION: '2.0',
        ns.STATUS: "418 I'm a teapot",
        ns.BODY: b'contents',
    })
    return reply


@pytest.fixture(scope='function')
def action_command(command):
    """Get a command payload for a service action call."""

    from kusanagi.sdk.lib.payload import ns

    address = 'http://1.2.3.4:77'
    service = 'foo'
    version = '1.0.0'
    action = 'bar'
    command.set([ns.PARAMS], [{
        ns.NAME: 'foo',
        ns.VALUE: 'bar',
    }])
    command.set([ns.TRANSPORT], {
        ns.META: {
            ns.GATEWAY: ['1.2.3.4:1234', 'http://1.2.3.4:77'],
            ns.ORIGIN: [service, version, action],
        },
        ns.FILES: {
            address: {
                service: {
                    version: {
                        action: [{
                            ns.NAME: 'foo',
                        }]
                    }
                }
            }
        },
    })
    return command


@pytest.fixture(scope='function')
def service_schema():
    """Get a service schema payload."""

    from kusanagi.sdk.lib.payload import ns
    from kusanagi.sdk.lib.payload.service import ServiceSchemaPayload

    payload = {
        ns.ADDRESS: '6.6.6.6:77',
        ns.FILES: True,
        ns.ACTIONS: {
            'foo': {},
        },
        ns.HTTP: {
            ns.GATEWAY: False,
            ns.BASE_PATH: '/test',
        },
    }
    return ServiceSchemaPayload(payload, name='foo', version='1.0.0')


@pytest.fixture(scope='session')
def AsyncMock():
    """
    Mock class that support asyncio.

    NOTE: AsyncMock support exists from python >= 3.8 in "unittest.mock.AsyncMock.

    """

    from unittest.mock import MagicMock

    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)

    return AsyncMock
