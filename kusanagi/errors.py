# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


class KusanagiError(Exception):
    """Base exception for KUSANAGI errors."""

    message = None

    def __init__(self, message=None):
        if message:
            self.message = message

        super().__init__(self.message)

    def __str__(self):
        return self.message or self.__class__.__name__


class KusanagiTypeError(KusanagiError):
    """Kusanagi type error."""
