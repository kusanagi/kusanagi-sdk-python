import pytest

from kusanagi.errors import KusanagiError


def test_kusanagi_error():
    error = KusanagiError()

    # By default no message is used
    assert error.message is None
    # Class name is used as default string for error
    assert str(error) == 'KusanagiError'

    # Create a new error with a message
    message = 'Test error message'
    error = KusanagiError(message)
    assert error.message == message
    assert str(error) == message


def test_kusanagi_error_subclass():
    # Define an error subclass with a default mesage
    class TestError(KusanagiError):
        message = 'Custom error message'

    error = TestError()
    assert error.message == TestError.message
    assert str(error) == TestError.message

    # When a message is give it overrides default one
    message = 'Another custom mesage'
    error = TestError(message)
    assert error.message == message
    assert str(error) == message
    # Error message is not the default one
    assert error.message != TestError.message
