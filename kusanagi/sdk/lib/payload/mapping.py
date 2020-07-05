# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import Iterator

from ..version import VersionString
from . import Payload
from .service import ServiceSchemaPayload


class MappingPayload(Payload):
    """Handles operations on mappings payloads."""

    def get_services(self) -> Iterator[dict]:
        """Get service names and versions."""

        for service, versions in self.items():
            for version in versions.keys():
                yield {'name': service, 'version': version}

    def get_service_schema_payload(self, name: str, version: str) -> ServiceSchemaPayload:
        """
        Get the service schema payload for a service version.

        The version can be either a fixed version or a pattern that uses "*"
        and resolves to the higher version available that matches.

        :param name: The name of the service.
        :param version: The version of the service.

        :raises: LookupError

        """

        if name in self:
            versions = self[name]

            # When the version doesn't exist try to resolve the version pattern and get the closest
            # highest version from the ones registered in the mapping for the current service.
            if version not in versions:
                resolved_version = VersionString(version).resolve(versions.keys())
                if resolved_version:
                    version = resolved_version

            if version:
                return ServiceSchemaPayload(versions[version], name=name, version=version)

        raise LookupError(f'Cannot resolve schema for Service: "{name}" ({version})')
