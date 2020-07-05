# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import logging


def test_lib_logging_formatter():
    from kusanagi.sdk.lib.logging import KusanagiFormatter

    class Record(object):
        pass

    record = Record()
    record.created = 1485622839.2490458  # Non GMT timestamp
    assert KusanagiFormatter().formatTime(record) == '2017-01-28T17:00:39.249'


def test_lib_logging_value_to_log_string():
    from kusanagi.sdk.lib.logging import value_to_log_string

    # Define a dummy class
    class Dummy(object):
        def __repr__(self):
            return 'DUMMY'

    # Define a dummy function
    def dummy():
        pass

    assert value_to_log_string(None) == 'NULL'
    assert value_to_log_string(True) == 'TRUE'
    assert value_to_log_string(False) == 'FALSE'
    assert value_to_log_string('value') == 'value'
    assert value_to_log_string(b'value') == 'dmFsdWU='
    assert value_to_log_string(lambda: None) == 'anonymous'
    assert value_to_log_string(dummy) == '[function dummy]'

    # Dictionaries and list are serialized as pretty JSON
    assert value_to_log_string({'a': 1}) == '{\n  "a": 1\n}'
    assert value_to_log_string(['1', '2']) == '[\n  "1",\n  "2"\n]'

    # For unknown types 'repr()' is used to get log string
    assert value_to_log_string(Dummy()) == 'DUMMY'

    # Check maximum characters
    max_chars = 100000
    assert len(value_to_log_string('*' * max_chars)) == max_chars
    assert len(value_to_log_string('*' * (max_chars + 10))) == max_chars


def test_lib_logging_setup_kusanagi_loggingr(logs):
    from kusanagi.sdk.lib.logging import KusanagiFormatter

    # Root logger must use KusanagiFormatter
    assert len(logging.root.handlers) == 1
    assert isinstance(logging.root.handlers[0].formatter, KusanagiFormatter)

    # SDK logger must use KusanagiFormatter
    logger = logging.getLogger('kusanagi')
    assert len(logger.handlers) == 1
    assert logger.level == logging.DEBUG
    assert isinstance(logger.handlers[0].formatter, KusanagiFormatter)

    assert logging.getLogger('asyncio').level == logging.ERROR

    # Basic check for logging format
    message = 'Test message'
    logging.getLogger('kusanagi').info(message)
    out = logs.getvalue()
    assert len(out) > 0
    out_parts = out.split(' ')
    assert out_parts[0].endswith('Z')  # Time
    assert out_parts[1] == 'component'  # Component type
    assert out_parts[2] == 'name/version'  # Component name and version
    assert out_parts[3] == '(framework-version)'
    assert out_parts[4] == '[INFO]'  # Level
    assert out_parts[5] == '[SDK]'  # SDK prefix
    assert ' '.join(out_parts[6:]).strip() == message


def test_lib_logging_logger_debug(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.debug('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[DEBUG]' in output
    assert '\n' not in output


def test_lib_logging_logger_debug_rid(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.debug('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[DEBUG]' in output
    assert '|RID|' in output
    assert '\n' not in output


def test_lib_logging_logger_info(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.info('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[INFO]' in output
    assert '\n' not in output


def test_lib_logging_logger_info_rid(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.info('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[INFO]' in output
    assert '|RID|' in output
    assert '\n' not in output


def test_lib_logging_logger_warning(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.warning('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[WARNING]' in output
    assert '\n' not in output


def test_lib_logging_logger_warning_rid(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.warning('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[WARNING]' in output
    assert '|RID|' in output
    assert '\n' not in output


def test_lib_logging_logger_error(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.error('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '\n' not in output


def test_lib_logging_logger_error_rid(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.error('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '|RID|' in output
    assert '\n' not in output


def test_lib_logging_logger_critical(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.critical('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[CRITICAL]' in output
    assert '\n' not in output


def test_lib_logging_logger_critical_rid(logs):
    from kusanagi.sdk.lib.logging import Logger

    logger = Logger('kusanagi')
    logger.critical('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[CRITICAL]' in output
    assert '|RID|' in output
    assert '\n' not in output


def test_lib_logging_logger_exception(logs):
    from kusanagi.sdk.lib import cli
    from kusanagi.sdk.lib.logging import Logger

    cli.DEBUG = False
    logger = Logger('kusanagi')
    logger.exception('Test message')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '\n' not in output


def test_lib_logging_logger_exception_rid(logs):
    from kusanagi.sdk.lib import cli
    from kusanagi.sdk.lib.logging import Logger

    # Exception tracebacks are displayed when DEBUG is enabled
    cli.DEBUG = True
    logger = Logger('kusanagi')
    logger.exception('Test message', rid='RID')
    output = logs.getvalue().rstrip('\n')
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '|RID|' in output
    assert '\n' in output


def test_lib_logging_request_logger(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    assert logger.rid == 'RID'


def test_lib_logging_request_logger_debug(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.debug('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[DEBUG]' in output
    assert '|RID|' in output


def test_lib_logging_request_logger_info(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.info('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[INFO]' in output
    assert '|RID|' in output


def test_lib_logging_request_logger_warning(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.warning('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[WARNING]' in output
    assert '|RID|' in output


def test_lib_logging_request_logger_error(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.error('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '|RID|' in output


def test_lib_logging_request_logger_critical(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.critical('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[CRITICAL]' in output
    assert '|RID|' in output


def test_lib_logging_request_logger_exception(logs):
    from kusanagi.sdk.lib.logging import RequestLogger

    logger = RequestLogger('kusanagi', 'RID')
    logger.exception('Test message')
    output = logs.getvalue()
    assert 'Test message' in output
    assert '[ERROR]' in output
    assert '|RID|' in output
