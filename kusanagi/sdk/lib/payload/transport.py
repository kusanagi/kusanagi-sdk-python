# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from . import Payload
from . import ns
from .utils import file_to_payload
from .utils import merge_dictionary
from .utils import param_to_payload

if TYPE_CHECKING:
    from typing import Any
    from typing import List
    from typing import Union

    from ...file import File
    from ...param import Param
    from .reply import ReplyPayload


class TransportPayload(Payload):
    """Handles operations on transport payloads."""

    # The types are mapped to payload namespaces
    TRANSACTION_COMMIT = ns.COMMIT
    TRANSACTION_ROLLBACK = ns.ROLLBACK
    TRANSACTION_COMPLETE = ns.COMPLETE

    # Paths that can me merged from other transport payloads
    MERGEABLE_PATHS = (
        [ns.DATA],
        [ns.RELATIONS],
        [ns.LINKS],
        [ns.CALLS],
        [ns.TRANSACTIONS],
        [ns.ERRORS],
        [ns.BODY],
        [ns.FILES],
        [ns.META, ns.FALLBACKS],
        [ns.META, ns.PROPERTIES],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reply = None

    def set(self, path: list, value: Any, prefix: bool = True) -> bool:
        ok = super().set(path, value, prefix=prefix)
        if self._reply is not None:
            self._reply.set([ns.TRANSPORT] + path, value, prefix=prefix)

        return ok

    def append(self, path: list, value: Any, prefix: bool = True) -> bool:
        ok = super().append(path, value, prefix=prefix)
        if self._reply is not None:
            self._reply.append([ns.TRANSPORT] + path, value, prefix=prefix)

        return ok

    def extend(self, path: list, values: list, prefix: bool = True) -> bool:
        ok = super().extend(path, values, prefix=prefix)
        if self._reply is not None:
            self._reply.extend([ns.TRANSPORT] + path, values, prefix=prefix)

        return ok

    def delete(self, path: list, prefix: bool = True) -> bool:
        ok = super().delete(path, prefix=prefix)
        if self._reply is not None:
            self._reply.delete([ns.TRANSPORT] + path, prefix=prefix)

        return ok

    def merge_runtime_call_transport(self, transport: TransportPayload) -> bool:
        """
        Merge a transport returned from a run-time call into the current transport.

        :param transport: The transport payload to merge.

        :raises: TypeError

        """

        if not isinstance(transport, TransportPayload):
            raise TypeError(f'Invalid type to merge into transport: {transport.__class__}')

        for path in self.MERGEABLE_PATHS:
            # Get the value from the other transport
            src_value = transport.get(path)
            if src_value is None:
                continue

            # Get the value from the current transport and if is not available init it as a dictionary
            dest_value = self.get(path)
            if dest_value is None:
                dest_value = {}
                # NOTE: Skip overriden set to avoid changing the reply payload
                super().set(path, dest_value)

            merge_dictionary(src_value, dest_value)

        # Update the transport in the reply payload with the runtime transport
        if self._reply is not None:
            # TODO: See if we need to keep the transport updated, or we just need to update the
            #       transport in the reply, and only keep track of the new files and params in
            #       the transport payload class. Merging and deepcopying is expensive.
            self._reply.set([ns.TRANSPORT], copy.deepcopy(self))

        return True

    def get_public_gateway_address(self) -> str:
        """Get the public Gateway address."""

        return self.get([ns.META, ns.GATEWAY], ['', ''])[1]

    def set_reply(self, reply: ReplyPayload) -> TransportPayload:
        """
        Set the reply payload.

        :param reply: The reply payload.

        """

        self._reply = reply
        return self

    def set_download(self, file: File) -> bool:
        """
        Set a file for download.

        :param file: The file to use as download contents.

        """

        return self.set([ns.BODY], file_to_payload(file))

    def set_return(self, value: Any = None) -> bool:
        """
        Set the return value.

        :param value: The value to use as return value in the payload.

        """

        if self._reply is not None:
            return self._reply.set([ns.RETURN], value)

        return False

    def add_data(self, name: str, version: str, action: str, data: Union[dict, list]) -> bool:
        """
        Add transport payload data.

        When there is existing data in the payload it is not removed. The new data
        is appended to the existing data in that case.

        :param name: The name of the Service.
        :param version: The version of the Service.
        :param action: The name of the action.
        :param data: The data to add.

        """

        gateway = self.get_public_gateway_address()
        return self.append([ns.DATA, gateway, name, version, action], data)

    def add_relate_one(self, service: str, pk: str, remote: str, fk: str) -> bool:
        """
        Add a "one-to-one" relation.

        :param service: The name of the local service.
        :param pk: The primary key of the local entity.
        :param remote: The name of the remote service.
        :param fk: The primary key of the remote entity.

        """

        gateway = self.get_public_gateway_address()
        return self.set([ns.RELATIONS, gateway, service, pk, gateway, remote], fk)

    def add_relate_many(self, service: str, pk: str, remote: str, fks: List[str]) -> bool:
        """
        Add a "one-to-many" relation.

        :param service: The name of the local service.
        :param pk: The primary key of the local entity.
        :param remote: The name of the remote service.
        :param fks: The primary keys of the remote entity.

        """

        gateway = self.get_public_gateway_address()
        return self.set([ns.RELATIONS, gateway, service, pk, gateway, remote], fks)

    def add_relate_one_remote(self, service: str, pk: str, address: str, remote: str, fk: str) -> bool:
        """
        Add a remote "one-to-one" relation.

        :param service: The name of the local service.
        :param pk: The primary key of the local entity.
        :param address: The address of the remote Gateway.
        :param remote: The name of the remote service.
        :param fk: The primary key of the remote entity.

        """

        gateway = self.get_public_gateway_address()
        return self.set([ns.RELATIONS, gateway, service, pk, address, remote], fk)

    def add_relate_many_remote(self, service: str, pk: str, address: str, remote: str, fks: List[str]) -> bool:
        """
        Add a remote "one-to-one" relation.

        :param service: The name of the local service.
        :param pk: The primary key of the local entity.
        :param address: The address of the remote Gateway.
        :param remote: The name of the remote service.
        :param fks: The primary keys of the remote entity.

        """

        gateway = self.get_public_gateway_address()
        return self.set([ns.RELATIONS, gateway, service, pk, address, remote], fks)

    def add_link(self, service: str, link: str, uri: str) -> bool:
        """
        Add a link.

        :param service: The name of the Service.
        :param link: The link name.
        :param uri: The URI for the link.

        """

        gateway = self.get_public_gateway_address()
        return self.set([ns.LINKS, gateway, service, link], uri)

    def add_transaction(
        self,
        type_: str,
        service: str,
        version: str,
        action: str,
        target: str,
        params: List[Param] = None,
    ) -> bool:
        """
        Add a transaction to be called when the request succeeds.

        :param type_: The type of transaction.
        :param service: The name of the Service.
        :param version: The version of the Service.
        :param action: The name of the origin action.
        :param target: The name of the target action.
        :param params: Optional parameters for the transaction.

        :raises: ValueError

        """

        if type_ not in (self.TRANSACTION_COMMIT, self.TRANSACTION_ROLLBACK, self.TRANSACTION_COMPLETE):
            raise ValueError(f'Invalid transaction type value: {type_}')

        transaction = {
            ns.NAME: service,
            ns.VERSION: version,
            ns.CALLER: action,
            ns.ACTION: target,
        }

        if params:
            transaction[ns.PARAMS] = [param_to_payload(p) for p in params]

        return self.append([ns.TRANSACTIONS, type_], transaction)

    def add_call(
        self,
        service: str,
        version: str,
        action: str,
        callee_service: str,
        callee_version: str,
        callee_action: str,
        duration: int,
        params: List[Param] = None,
        files: List[File] = None,
        timeout: int = None,
        transport: TransportPayload = None,
    ) -> bool:
        """
        Add a run-time call.

        Current transport payload is used when the optional transport is not given.

        :param service: The name of the Service.
        :param version: The version of the Service.
        :param action: The name of the action making the call.
        :param callee_service: The called service.
        :param callee_version: The called version.
        :param callee_action: The called action.
        :param duration: The call duration.
        :param params: Optional parameters to send.
        :param files: Optional files to send.
        :param timeout: Optional timeout for the call.
        :param transport: Optional transport payload.

        :raises: ValueError

        """

        # Validate duration to make sure the calls is not treated as a deferred call by the framework
        if duration is None:
            raise ValueError('Duration is required when adding run-time calls to transport')

        call = {
            ns.NAME: callee_service,
            ns.VERSION: callee_version,
            ns.ACTION: callee_action,
            ns.CALLER: action,
            ns.DURATION: duration,
        }

        if params:
            call[ns.PARAMS] = [param_to_payload(p) for p in params]

        if files:
            call[ns.FILES] = [file_to_payload(f) for f in files]

        if timeout is not None:
            call[ns.TIMEOUT] = timeout

        # When a transport is present add the call to it and then merge it into the current transport
        if transport is not None:
            transport.append([ns.CALLS, service, version], call)
            return self.merge_runtime_call_transport(transport)

        # When there is no transport just add the call to current transport
        return self.append([ns.CALLS, service, version], call)

    def add_defer_call(
        self,
        service: str,
        version: str,
        action: str,
        callee_service: str,
        callee_version: str,
        callee_action: str,
        params: List[Param] = None,
        files: List[File] = None,
    ) -> bool:
        """
        Add a deferred call.

        :param service: The name of the Service.
        :param version: The version of the Service.
        :param action: The name of the action making the call.
        :param callee_service: The called service.
        :param callee_version: The called version.
        :param callee_action: The called action.
        :param params: Optional parameters to send.
        :param files: Optional files to send.

        """

        call = {
            ns.NAME: callee_service,
            ns.VERSION: callee_version,
            ns.ACTION: callee_action,
            ns.CALLER: action,
        }

        if params:
            call[ns.PARAMS] = [param_to_payload(p) for p in params]

        # TODO: Should the file be added to the call too ? Not in the specs.
        file_payloads = [file_to_payload(f) for f in files] if files else None
        if file_payloads:
            call[ns.FILES] = file_payloads

        # Add the call to the transport payload
        ok = self.append([ns.CALLS, service, version], call)
        # When there are files included in the call add them to the transport payload
        if ok and file_payloads:
            gateway = self.get_public_gateway_address()
            self.extend([ns.FILES, gateway, callee_service, callee_version, callee_action], file_payloads)

        return ok

    def add_remote_call(
        self,
        address: str,
        service: str,
        version: str,
        action: str,
        callee_service: str,
        callee_version: str,
        callee_action: str,
        params: List[Param] = None,
        files: List[File] = None,
        timeout: int = None,
    ) -> bool:
        """
        Add a run-time call.

        Current transport payload is used when the optional transport is not given.

        :param address: The address of the remote Gateway.
        :param service: The name of the Service.
        :param version: The version of the Service.
        :param action: The name of the action making the call.
        :param callee_service: The called service.
        :param callee_version: The called version.
        :param callee_action: The called action.
        :param params: Optional parameters to send.
        :param files: Optional files to send.
        :param timeout: Optional timeout for the call.

        """

        call = {
            ns.GATEWAY: address,
            ns.NAME: callee_service,
            ns.VERSION: callee_version,
            ns.ACTION: callee_action,
            ns.CALLER: action,
        }

        if timeout is not None:
            call[ns.TIMEOUT] = timeout

        if params:
            call[ns.PARAMS] = [param_to_payload(p) for p in params]

        # TODO: Should the file be added to the call too ? Not in the specs.
        file_payloads = [file_to_payload(f) for f in files] if files else None
        if file_payloads:
            call[ns.FILES] = file_payloads

        # Add the call to the transport payload
        ok = self.append([ns.CALLS, service, version], call)
        # When there are files included in the call add them to the transport payload
        if ok and file_payloads:
            gateway = self.get_public_gateway_address()
            self.extend([ns.FILES, gateway, callee_service, callee_version, callee_action], file_payloads)

        return ok

    def add_error(self, service: str, version: str, message: str, code: int, status: str) -> bool:
        """
        Add a Service error.

        :param service: The name of the Service.
        :param version: The version of the Service.
        :param message: The error message.
        :param code: The error code.
        :param status: The status message for the protocol.

        """

        gateway = self.get_public_gateway_address()
        return self.append([ns.ERRORS, gateway, service, version], {
            ns.MESSAGE: message,
            ns.CODE: code,
            ns.STATUS: status,
        })

    def has_calls(self, service: str, version: str) -> bool:
        """
        Check if there are any type of calls registered for a Service.

        :param service: The name of the Service.
        :param version: The version of the Service.

        """

        for call in self.get([ns.CALLS, service, version], []):
            # When duration is None or there is no duration it means the call was not
            # executed so is safe to assume a call that has to be executed was found.
            if call.get(ns.DURATION) is None:
                return True

        return False

    def has_files(self) -> bool:
        """Check if there are files registered in the transport."""

        return self.exists([ns.FILES])

    def has_transactions(self) -> bool:
        """Check if there are transactions registered in the transport."""

        return self.exists([ns.TRANSACTIONS])

    def has_download(self) -> bool:
        """Check if there is a file download registered in the transport."""

        return self.exists([ns.BODY])
