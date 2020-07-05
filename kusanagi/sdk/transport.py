# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import json
from typing import Iterator
from typing import List

from .caller import Caller
from .error import Error
from .file import File
from .lib.payload import ns
from .lib.payload.transport import TransportPayload
from .lib.payload.utils import payload_to_file
from .link import Link
from .relation import Relation
from .servicedata import ServiceData
from .transaction import Transaction


class Transport(object):
    """Transport class encapsulates the transport object."""

    def __init__(self, payload: TransportPayload):
        """
        Constructor.

        :param payload: The transport payload.

        """

        self.__payload = payload

    def __str__(self):  # pragma: no cover
        return str(self.__payload)

    def get_request_id(self) -> str:
        """Get the request UUID."""

        return self.__payload.get([ns.META, ns.ID], '')

    def get_request_timestamp(self) -> str:
        """Get the request creation timestamp."""

        return self.__payload.get([ns.META, ns.DATETIME], '')

    def get_origin_service(self) -> tuple:
        """
        Get the origin of the request.

        Result is an array containing name, version and action
        of the service that was the origin of the request.

        """

        return tuple(self.__payload.get([ns.META, ns.ORIGIN], []))

    def get_origin_duration(self) -> int:
        """
        Get the service execution time in milliseconds.

        This time is the number of milliseconds spent by the service that was the origin of the request.

        """

        return self.__payload.get([ns.META, ns.DURATION], 0)

    def get_property(self, name: str, default: str = '') -> str:
        """
        Get a userland property value.

        The name of the property is case sensitive.

        An empty string is returned when a property with the specified
        name does not exist, and no default value is provided.

        :param name: The name of the property.
        :param default: The default value to use when the property doesn't exist.

        :raises: TypeError

        """

        if not isinstance(default, str):
            raise TypeError('Default value must be a string')

        return self.__payload.get([ns.META, ns.PROPERTIES, name], default)

    def get_properties(self) -> dict:
        """Get all the properties defined in the transport."""

        return dict(self.__payload.get([ns.META, ns.PROPERTIES], {}))

    def has_download(self) -> bool:
        """Check if a file download has been registered for the response."""

        return self.__payload.exists([ns.BODY])

    def get_download(self) -> File:
        """Get the file download defined for the response."""

        if self.has_download():
            return payload_to_file(self.__payload.get([ns.BODY]))
        else:
            return File('')

    def get_data(self) -> Iterator[ServiceData]:
        """
        Get the transport data.

        An empty list is returned when there is no data in the transport.

        """

        data = self.__payload.get([ns.DATA], {})
        for address, services in data.items():
            for service, versions in services.items():
                for version, actions in versions.items():
                    yield ServiceData(address, service, version, actions)

    def get_relations(self) -> Iterator[Relation]:
        """
        Get the service relations.

        An empty list is returned when there are no relations defined in the transport.

        """

        data = self.__payload.get([ns.RELATIONS], {})
        for address, services in data.items():
            for service, pks in services.items():
                for pk, foreign_services in pks.items():
                    yield Relation(address, service, pk, foreign_services)

    def get_links(self) -> Iterator[Link]:
        """
        Get the service links.

        An empty list is returned when there are no links defined in the transport.

        """

        data = self.__payload.get([ns.LINKS], {})
        for address, services in data.items():
            for service, references in services.items():
                for ref, uri in references.items():
                    yield Link(address, service, ref, uri)

    def get_calls(self) -> Iterator[Caller]:
        """
        Get the service calls.

        An empty list is returned when there are no calls defined in the transport.

        """

        data = self.__payload.get([ns.CALLS], {})
        for service, versions in data.items():
            for version, callees in versions.items():
                for callee in callees:
                    action = callee[ns.CALLER]
                    yield Caller(service, version, action, callee)

    def get_transactions(self, type_: str) -> List[Transaction]:
        """
        Get the transactions

        The transaction type is case sensitive, and supports "commit", "rollback" or "complete" as value.

        An empty list is returned when there are no transactions defined in the transport.

        :param type_: The transaction type.

        :raises: ValueError

        """

        if type_ not in Transaction.TYPE_CHOICES:
            raise ValueError(type_)

        # Mapping between user types and payload short names
        types = {
            Transaction.TYPE_COMMIT: TransportPayload.TRANSACTION_COMMIT,
            Transaction.TYPE_ROLLBACK: TransportPayload.TRANSACTION_ROLLBACK,
            Transaction.TYPE_COMPLETE: TransportPayload.TRANSACTION_COMPLETE,
        }

        data = self.__payload.get([ns.TRANSACTIONS, types[type_]], [])
        return [Transaction(type_, trx) for trx in data]

    def get_errors(self) -> Iterator[Error]:
        """
        Get transport errors.

        An empty list is returned when there are no errors defined in the transport.

        """

        data = self.__payload.get([ns.ERRORS], {})
        for address, services in data.items():
            for service, versions in services.items():
                for version, errors in versions.items():
                    for error in errors:
                        message = error.get(ns.MESSAGE, Error.DEFAULT_MESSAGE)
                        code = error.get(ns.CODE, Error.DEFAULT_CODE)
                        status = error.get(ns.STATUS, Error.DEFAULT_STATUS)
                        yield Error(address, service, version, message, code, status)
