# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import logging
from typing import Callable

LOG = logging.getLogger(__name__)


class Events(object):
    """Handles component events."""

    def __init__(self, on_startup: Callable, on_shutdown: Callable, on_error: Callable):
        """
        Constructor.

        :param on_startup: Callback to execute when startup is called.
        :param on_shutdown: Callback to execute when shutdown is called.
        :param on_error: Callback to execute when error is called.

        """

        self.__on_startup = on_startup
        self.__on_shutdown = on_shutdown
        self.__on_error = on_error

    def startup(self, *args, **kwargs) -> bool:
        """Call the startup callback."""

        if self.__on_startup:
            LOG.info('Running startup callback...')
            try:
                self.__on_startup(*args, **kwargs)
            except Exception as exc:
                LOG.error(f'Startup callback failed: {exc}')
                return False

        return True

    def shutdown(self, *args, **kwargs) -> bool:
        """Call the shutdown callback."""

        if self.__on_shutdown:
            LOG.info('Running shutdown callback...')
            try:
                self.__on_shutdown(*args, **kwargs)
            except Exception as exc:
                LOG.error(f'Shutdown callback failed: {exc}')
                return False

        return True

    def error(self, *args, **kwargs) -> bool:
        """Call the error callback."""

        if self.__on_error:
            LOG.info('Running error callback...')
            try:
                self.__on_error(*args, **kwargs)
            except Exception as exc:
                LOG.error(f'Error callback failed: {exc}')
                return False

        return True
