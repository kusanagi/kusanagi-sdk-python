# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


def test_lib_version_is_valid():
    from kusanagi.sdk.lib.version import VersionString

    assert VersionString.is_valid('1.0.1')
    assert VersionString.is_valid('*')
    assert VersionString.is_valid('1.0.*')
    assert VersionString.is_valid('1.*')
    # The @ is not a valid version pattern character
    assert not VersionString.is_valid('1.0.@')


def test_lib_version_simple_match():
    """Check versions matches for a fixed version string."""

    from kusanagi.sdk.lib.version import VersionString

    # Create a version string without wildcards
    version_string = VersionString('1.2.3')
    # Versions match
    assert version_string.match('1.2.3')
    # Versions doesn't match
    assert not version_string.match('A.B.C')
    # Invalid versions also doesn't match
    assert not version_string.match('A.B.@')


def test_lib_version_wildcards_match():
    """Check versions matches for a version pattern with wildcards."""

    from kusanagi.sdk.lib.version import VersionString

    # Create a version with wildcards
    version_string = VersionString('1.*.*')

    # iValid versions match
    for version in ('1.2.3', '1.4.3', '1.2.3-alpha'):
        assert version_string.match(version)

    # Invalid versions don't match
    for version in ('A.B.C', '2.2.3'):
        assert not version_string.match(version)


def test_lib_version_invalid_match():
    """Check versions matches for a version pattern that is invalid."""

    from kusanagi.sdk.lib.version import VersionString

    # Create a version that is not valid
    version_string = VersionString('1.@.1')

    # Valid and invalid versions won't match
    for version in ('1.2.3', '1.4.3', '1.2.3-alpha', 'A.B.C', '2.2.3'):
        assert not version_string.match(version)


def test_lib_version_compare_none():
    """Check none comparison results."""

    from kusanagi.sdk.lib.version import EQUAL
    from kusanagi.sdk.lib.version import GREATER
    from kusanagi.sdk.lib.version import compare_none

    assert compare_none(None, None) == EQUAL
    # Version with less parts is higher, which means
    # None is higher than a non None "part" value.
    assert compare_none('A', None) == GREATER


def test_lib_version_compare_sub_part():
    """Check comparison results for version string sub parts."""

    from kusanagi.sdk.lib.version import EQUAL
    from kusanagi.sdk.lib.version import GREATER
    from kusanagi.sdk.lib.version import LOWER
    from kusanagi.sdk.lib.version import compare_sub_parts

    # Parts are equal
    assert compare_sub_parts('A', 'A') == EQUAL

    # First part is greater than second one
    assert compare_sub_parts('B', 'A') == LOWER
    assert compare_sub_parts('2', '1') == LOWER
    # First part is lower than second one
    assert compare_sub_parts('A', 'B') == GREATER
    assert compare_sub_parts('1', '2') == GREATER

    # Integer parts are always lower than string parts ...

    # Second part is greater than first one
    assert compare_sub_parts('A', '1') == GREATER
    # Second part is lower than first one
    assert compare_sub_parts('1', 'A') == LOWER


def test_lib_version_compare():
    """Check comparisons between different versions."""

    from kusanagi.sdk.lib.version import EQUAL
    from kusanagi.sdk.lib.version import GREATER
    from kusanagi.sdk.lib.version import LOWER
    from kusanagi.sdk.lib.version import compare

    cases = (
        ('A.B.C', LOWER, 'A.B'),
        ('A.B-beta', LOWER, 'A.B'),
        ('A.B-beta', LOWER, 'A.B-gamma'),
        ('A.B.C', EQUAL, 'A.B.C'),
        ('A.B-alpha', EQUAL, 'A.B-alpha'),
        ('A.B', GREATER, 'A.B.C'),
        ('A.B', GREATER, 'A.B-alpha'),
        ('A.B-beta', GREATER, 'A.B-alpha'),
    )

    for ver2, expected, ver1 in cases:
        assert compare(ver1, ver2) == expected


def test_lib_version_resolve():
    """Check version pattern resolution."""

    from kusanagi.sdk.lib.version import VersionString

    # Format: pattern, expected, versions
    cases = (
        ('*', '3.4.1', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.*', '3.4.1', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.4.1', '3.4.1', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.4.*', '3.4.1', ('3.4.0', '3.4.1', '3.4.a')),
        ('3.4.*', '3.4.1', ('3.4.a', '3.4.1', '3.4.0')),
        ('3.4.*', '3.4.gamma', ('3.4.alpha', '3.4.beta', '3.4.gamma')),
        ('3.4.*', '3.4.gamma', ('3.4.alpha', '3.4.a', '3.4.gamma')),
        ('3.4.*', '3.4.12', ('3.4.a', '3.4.12', '3.4.1')),
        ('3.4.*', '3.4.0', ('3.4.0', '3.4.0-a', '3.4.0-0')),
        ('3.4.*', '3.4.0-1', ('3.4.0-0', '3.4.0-a', '3.4.0-1')),
        ('3.4.*', '3.4.0-1', ('3.4.0-0', '3.4.0-1-0', '3.4.0-1')),
    )

    for pattern, expected, versions in cases:
        # Compare pattern against all versions
        version_string = VersionString(pattern)
        for version in versions:
            assert version_string.resolve(versions) == expected

    # Check for a non maching pattern
    assert VersionString('3.4.*.*').resolve(['1.0', 'A.B.C.D', '3.4.1']) == ''
