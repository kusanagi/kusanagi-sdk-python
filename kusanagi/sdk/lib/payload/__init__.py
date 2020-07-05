# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import Any

from .. import json


class Payload(dict):
    """
    Handles operations on the transmitted data.

    Payloads behaves like an ordered dictionary, and their contents
    can be traversed using paths.

    """

    # Prefix to add to any path
    path_prefix = None

    def __str__(self):
        # Serialize the payload as a formatted JSON string
        return json.dumps(self, prettify=True).decode('utf8')

    def exists(self, path: list, prefix: bool = True) -> bool:
        """
        Check if a path exists in the payload.

        :param path: Path to traverse.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        for name in path:
            try:
                item = item[name]
            except (TypeError, KeyError):
                break
        else:
            # Return true when the full path is traversed
            return True

        return False

    def equals(self, path: list, value: Any, prefix: bool = True) -> bool:
        """
        Check if a value exists in the payload.

        :param path: Path to traverse.
        :param value: The value to check in the given path.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        for name in path:
            try:
                item = item[name]
            except (TypeError, KeyError):
                break
        else:
            # When the full path is traversed compare the value
            return item == value

        return False

    def get(self, path: list, default: Any = None, prefix: bool = True) -> Any:
        """
        Get a value from the payload.

        :param path: Path to traverse.
        :param default: Optional value to return when the path doesn't exist.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        for name in path:
            try:
                item = item[name]
            except (TypeError, KeyError):
                break
        else:
            return item

        return default

    def set(self, path: list, value: Any, prefix: bool = True) -> bool:
        """
        Set a value in the payload.

        :param path: Path where to set the value.
        :param value: The value to set.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        last_index = len(path) - 1
        for i, name in enumerate(path):
            # When the element is the last use the value as default otherwise
            # use a dictionary to be able to keep traversing the path.
            try:
                if i == last_index:
                    item[name] = value
                else:
                    item = item.setdefault(name, {})
            except (AttributeError, TypeError):
                # The path contains an element that is not a dictionary
                return False

        return True

    def append(self, path: list, value: Any, prefix: bool = True) -> bool:
        """
        Append a value to a list in the payload.

        A new list is created for the given path when a value doesn't
        exist for that path.

        The value is appended when a list already exist for the path.

        :param path: Path where to append the value.
        :param value: The value to append.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        last_index = len(path) - 1
        for i, name in enumerate(path):
            try:
                if i == last_index:
                    # When the last element is traversed append the value.
                    # Values must be a list to be able to append it.
                    values = item.setdefault(name, [])
                    if isinstance(values, list):
                        values.append(value)
                        return True
                else:
                    item = item.setdefault(name, {})
            except (AttributeError, TypeError):
                # The path contains an element that is not a dictionary
                break

        return False

    def extend(self, path: list, values: list, prefix: bool = True) -> bool:
        """
        Extend a list value by appending the elements of another list.

        A new list is created for the given path when a value doesn't
        exist for that path.

        The values are appended when a list already exist for the path.

        :param path: Path where to append the values.
        :param values: The values to append.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        item = self
        last_index = len(path) - 1
        for i, name in enumerate(path):
            try:
                if i == last_index:
                    # When the last element is traversed append the values.
                    # Current values must be a list to be able to append it.
                    current_values = item.setdefault(name, [])
                    if isinstance(current_values, list):
                        current_values.extend(values)
                        return True
                else:
                    item = item.setdefault(name, {})
            except (AttributeError, TypeError):
                # The path contains an element that is not a dictionary
                break

        return False

    def delete(self, path: list, prefix: bool = True) -> bool:
        """
        Delete a value from the payload.

        Only the last element of the path is deleted from the payload.

        :param path: Path to traverse.
        :param prefix: Optional flag to disable path prefixing.

        """

        if prefix and self.path_prefix:
            path = self.path_prefix + path

        *path, name = path
        # NOTE: The value of path is a list
        element = self.get(path, None, prefix=False)
        if not isinstance(element, dict) or name not in element:
            return False

        del element[name]
        return True
