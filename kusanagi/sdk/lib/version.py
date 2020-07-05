# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import re
from functools import cmp_to_key
from itertools import zip_longest
from typing import List

# Regexp to check version pattern for invalid chars
INVALID_PATTERN = re.compile(r'[^a-zA-Z0-9*.,_-]')

# Regexp to remove duplicated '*' from version
WILDCARDS = re.compile(r'\*+')

# Regexp to match version dot separators
VERSION_DOTS = re.compile(r'([^*])\.')

# Regexp to match all wildcards except the last one
VERSION_WILDCARDS = re.compile(r'\*+([^$])')

# Values to return when using comparison functions
GREATER = 1
EQUAL = 0
LOWER = -1


def compare_none(part1: str, part2: str) -> int:
    if part1 == part2:
        return EQUAL
    elif part2 is None:
        # The one that DO NOT have more parts is greater
        return GREATER
    else:
        return LOWER


def compare_sub_parts(sub1: str, sub2: str) -> int:
    # Sub parts are equal
    if sub1 == sub2:
        return EQUAL

    # Check if any sub part is an integer
    is_integer = [False, False]
    for idx, value in enumerate((sub1, sub2)):
        try:
            int(value)
        except ValueError:
            is_integer[idx] = False
        else:
            is_integer[idx] = True

    # Compare both sub parts according to their type
    if is_integer[0] != is_integer[1]:
        # One is an integer. The integer is higher than the non integer.
        # Check if the first sub part is an integer, and if so it means
        # sub2 is lower than sub1.
        return LOWER if is_integer[0] else GREATER

    # Both sub parts are of the same type
    return GREATER if sub1 < sub2 else LOWER


def compare(ver1: str, ver2: str) -> int:
    # Versions are equal
    if ver1 == ver2:
        return EQUAL

    for part1, part2 in zip_longest(ver1.split('.'), ver2.split('.')):
        # One of the parts is None
        if part1 is None or part2 is None:
            return compare_none(part1, part2)

        for sub1, sub2 in zip_longest(part1.split('-'), part2.split('-')):
            # One of the sub parts is None
            if sub1 is None or sub2 is None:
                # Sub parts are different, because one have a
                # value and the other not.
                return compare_none(sub1, sub2)

            # Both sub parts have a value
            result = compare_sub_parts(sub1, sub2)
            if result:
                # Sub parts are not equal
                return result


class VersionString(object):
    """Semantic version string."""

    def __init__(self, pattern: str):
        # Remove duplicated wildcards from version pattern
        self.__version = WILDCARDS.sub('*', pattern)

        if '*' in self.__version:
            # Create an expression for version pattern comparisons
            expr = VERSION_WILDCARDS.sub(r'[^*.]+\1', self.__version)
            # Escape dots to work with the regular expression
            expr = VERSION_DOTS.sub(r'\1\.', expr)

            # If there is a final wildcard left replace it with an
            # expression to match any characters after the last dot.
            if expr[-1] == '*':
                expr = expr[:-1] + '.*'

            # Create a pattern to be use for cmparison
            self.__pattern = re.compile(expr)
        else:
            self.__pattern = None

    def __repr__(self):  # pragma: no cover
        return f'<VersionString({self.__version})>'

    def __str__(self):  # pragma: no cover
        return self.__version

    @staticmethod
    def is_valid(pattern: str) -> bool:
        """
        Check if a version pattern is valid.

        :param pattern: A version pattern to validate.

        """

        return INVALID_PATTERN.search(pattern) is None

    def match(self, version: str) -> bool:
        """
        Check if a version matches the current version pattern.

        :param version: A version to check agains the current pattern.

        """

        # Check that the version pattern is valid
        if not self.is_valid(self.__version):
            return False

        if not self.__pattern:
            return self.__version == version
        else:
            return self.__pattern.fullmatch(version) is not None

    def resolve(self, versions: List[str]) -> str:
        """
        Resolve the highest compatible version to the current version pattern.

        An empty string is returned when the no version is resolved.

        :param versions: List of versions to resolve against the current pattern.

        """

        valid_versions = [ver for ver in versions if self.match(ver)]
        if not valid_versions:
            return ''

        valid_versions.sort(key=cmp_to_key(compare))
        return valid_versions[0]
