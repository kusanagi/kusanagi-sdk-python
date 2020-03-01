# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from kusanagi.errors import KusanagiError

# Protocols
HTTP = 'urn:kusanagi:protocol:http'
KTP = 'urn:kusanagi:protocol:ktp'


def url(protocol, address):
    """Create a URL for a protocol.

    :param protocol: URN for a protocol.
    :type protocol: str
    :param address: An IP address. It can include a port.
    :type address: str

    :raises: KusanagiError

    :rtype: str

    """

    if protocol == HTTP:
        return 'http://{}'.format(address)
    elif protocol == KTP:
        return 'ktp://{}'.format(address)
    else:
        raise KusanagiError('Unknown protocol: {}'.format(protocol))
