# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import base64
import logging
import sys
import time
import types
from datetime import datetime
from typing import Any

from . import json

LOG = logging.getLogger(__name__)

# Syslog numeric levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
NOTICE = WARNING + 1
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
ALERT = CRITICAL + 1
EMERGENCY = ALERT + 1

# Mappings between Syslog numeric severity levels and python logging levels
SYSLOG_NUMERIC = {
    0: EMERGENCY,
    1: ALERT,
    2: logging.CRITICAL,
    3: logging.ERROR,
    4: NOTICE,
    5: logging.WARNING,
    6: logging.INFO,
    7: logging.DEBUG,
}


class Logger(object):
    """
    KUSANAGI logger with request ID support.

    The logger methods support and optional keyword "rid" to send the current
    request ID. If the request ID is valid it is added as suffix to the log message.

    """

    def __init__(self, name: str):
        """
        Constructor.

        :param name: The logger name.

        """

        self.__logger = logging.getLogger(name)

    def __format(self, message: str, rid: str) -> str:
        # When there is no request ID return the message unchanged
        if not rid:
            return message

        # Add the request ID as suffix for the log message
        return f'{message} |{rid}|'

    def debug(self, message: str, *args, **kwargs):
        self.__logger.debug(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.__logger.info(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.__logger.warning(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.__logger.error(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self.__logger.critical(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        from . import cli

        # When debug mode is enabled displat traceback, otherwise log only the message
        # as an error without stack trace. This is important because normally each log
        # should be a single line to avoid breaking log parsers. Debug mode is usually
        # enabled during testing and development.
        if cli.DEBUG:
            self.__logger.exception(self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)
        else:
            self.error(message, *args, **kwargs)

    def log(self, level: int, message: str, *args, **kwargs):
        self.__logger.log(level, self.__format(message, kwargs.pop('rid', '')), *args, **kwargs)


class RequestLogger(Logger):
    """
    Logger for requests.

    It appends the request ID to all logging messages.

    """

    def __init__(self, name: str, rid: str):
        """
        Constructor.

        :param name: The logger name.
        :param rid: The ID of the current request.

        """

        super().__init__(name)
        # When the request ID is not valid use a "-" to avoid breaking the
        # log format in case there is a tool being used to parse the SDK logs.
        self.__rid = rid or '-'

    @property
    def rid(self) -> str:
        return self.__rid

    def debug(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().exception(*args, **kwargs)

    def log(self, *args, **kwargs):
        kwargs['rid'] = self.__rid
        super().log(*args, **kwargs)


class KusanagiFormatter(logging.Formatter):
    """Default KUSANAGI logging formatter."""

    def formatTime(self, record: logging.LogRecord, *args, **kwargs) -> str:
        utc = time.mktime(time.gmtime(record.created)) + (record.created % 1)
        return datetime.fromtimestamp(utc).isoformat()[:-3]


def value_to_log_string(value: Any, max_chars: int = 100000) -> str:
    """
    Convert a value to a string.

    :param value: A value to log.
    :param max_chars: Optional maximum number of characters to return.

    """

    if value is None:
        output = 'NULL'
    elif isinstance(value, bool):
        output = 'TRUE' if value else 'FALSE'
    elif isinstance(value, str):
        output = value
    elif isinstance(value, bytes):
        # Binary data is logged as base64
        output = base64.b64encode(value).decode('utf8')
    elif isinstance(value, (dict, list, tuple)):
        output = json.dumps(value, prettify=True).decode('utf8')
    elif isinstance(value, types.FunctionType):
        output = 'anonymous' if value.__name__ == '<lambda>' else f'[function {value.__name__}]'
    else:
        output = repr(value)

    return output[:max_chars]


def get_output_buffer():  # pragma: no cover
    """Get buffer interface to send logging output."""

    return sys.stdout


def disable_logging():  # pragma: no cover
    """Disable all logs."""

    logging.disable(sys.maxsize)


def setup_kusanagi_logging(type_: str, name: str, version: str, framework: str, level: int):
    """
    Initialize logging defaults for KUSANAGI.

    :param type_: Component type.
    :param name: Component name.
    :param version: Component version.
    :param framework: KUSANAGI framework version.
    :param level: Logging level.

    """

    # Add new logging levels to follow KUSANAGI SDK specs
    logging.addLevelName(NOTICE, 'NOTICE')
    logging.addLevelName(ALERT, 'ALERT')
    logging.addLevelName(EMERGENCY, 'EMERGENCY')

    # Define the format to use as prefix for all log messages
    fmt = f'%(asctime)sZ {type_} {name}/{version} ({framework}) [%(levelname)s] [SDK] %(message)s'

    # Setup root logger
    output = get_output_buffer()
    root = logging.root
    if not root.handlers:
        logging.basicConfig(level=level, stream=output)
        root.setLevel(level)
        root.handlers[0].setFormatter(KusanagiFormatter(fmt))

    # Setup kusanagi loggers
    logger = logging.getLogger('kusanagi')
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=output)
        handler.setFormatter(KusanagiFormatter(fmt))
        logger.addHandler(handler)
        logger.propagate = False

    # Setup other loggers
    logger = logging.getLogger('asyncio')
    logger.setLevel(logging.ERROR)
