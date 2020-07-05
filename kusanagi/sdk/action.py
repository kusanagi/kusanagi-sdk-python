# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import annotations

import copy
from decimal import Decimal
from typing import TYPE_CHECKING

from .api import Api
from .file import File
from .file import FileSchema
from .file import validate_file_list
from .lib import datatypes
from .lib.call import Client
from .lib.error import KusanagiError
from .lib.payload import ns
from .lib.payload.error import ErrorPayload
from .lib.payload.transport import TransportPayload
from .lib.payload.utils import payload_to_file
from .lib.payload.utils import payload_to_param
from .lib.version import VersionString
from .param import Param
from .param import ParamSchema
from .param import validate_parameter_list

if TYPE_CHECKING:
    from typing import Any
    from typing import List

    from .lib.payload.action import ActionSchemaPayload
    from .lib.payload.action import HttpActionSchemaPayload


# Default action execution timeout in milliseconds
EXECUTION_TIMEOUT = 30000

# Valid types for the action return values
RETURN_TYPES = {
    datatypes.TYPE_NULL: (type(None), ),
    datatypes.TYPE_BOOLEAN: (bool, ),
    datatypes.TYPE_INTEGER: (int, ),
    datatypes.TYPE_FLOAT: (float, Decimal),
    datatypes.TYPE_STRING: (str, ),
    datatypes.TYPE_BINARY: (str, ),
    datatypes.TYPE_ARRAY: (list, ),
    datatypes.TYPE_OBJECT: (dict, ),
}

# Default return values
DEFAULT_RETURN_VALUES = {
    datatypes.TYPE_NULL: None,
    datatypes.TYPE_BOOLEAN: False,
    datatypes.TYPE_INTEGER: 0,
    datatypes.TYPE_FLOAT: 0.0,
    datatypes.TYPE_STRING: '',
    datatypes.TYPE_BINARY: '',
    datatypes.TYPE_ARRAY: [],
    datatypes.TYPE_OBJECT: {},
}


class Action(Api):
    """Action API class for service component."""

    def __init__(self, *args, **kwargs):
        """Constructor."""

        super().__init__(*args, **kwargs)
        # Copy the command transport without keeping references to avoid changing
        # the transport data in the command when the action changes the transport.
        # This leaves a "vanilla" transport inside the command, to be used as base
        # transport for the runtime calls.
        payload = copy.deepcopy(self._command.get([ns.TRANSPORT], {}))
        self._transport = TransportPayload(payload)
        self._transport.set_reply(self._reply)

        # Index the files for the current action by name
        gateway = self._transport.get([ns.META, ns.GATEWAY], ['', ''])[1]
        path = [ns.FILES, gateway, self.get_name(), self.get_version(), self.get_action_name()]
        self.__files = {file[ns.NAME]: file for file in self._transport.get(path, [])}

        # Index parameters by name
        self.__params = {param[ns.NAME]: param for param in self._command.get([ns.PARAMS], [])}

        # Set a default return value for the action when there are schemas
        if self._schemas:
            try:
                schema = self.get_service_schema(self.get_name(), self.get_version())
                action_schema = schema.get_action_schema(self.get_action_name())
                if action_schema.has_return():
                    return_type = action_schema.get_return_type()
                    self._transport.set_return(DEFAULT_RETURN_VALUES[return_type])
            except Exception:  # pragma: no cover
                pass

    def is_origin(self) -> bool:
        """Check if the current service is the origin of the request."""

        origin = [self.get_name(), self.get_version(), self.get_action_name()]
        return self._reply.get([ns.TRANSPORT, ns.META, ns.ORIGIN]) == origin

    def get_action_name(self) -> str:
        """Get the name of the action."""

        return self._state.action

    def set_property(self, name: str, value: str) -> Action:
        """
        Set a userland property in the transport with the given name and value.

        :param name: The property name.
        :param value: The property value.

        :raises: TypeError

        """

        if not isinstance(value, str):
            raise TypeError('Value is not a string')

        self._reply.set([ns.TRANSPORT, ns.META, ns.PROPERTIES, name], value)
        return self

    def has_param(self, name: str) -> bool:
        """
        Check if a parameter exists.

        :param name: The parameter name.

        """

        return name in self.__params

    def get_param(self, name: str) -> Param:
        """
        Get an action parameter.

        :param name: The parameter name.

        """

        # TODO: Create the params from the service schema (see PHP SDK)
        if not self.has_param(name):
            return Param(name)

        return payload_to_param(self.__params[name])

    def get_params(self) -> List[Param]:
        """Get all action parameters."""

        return [payload_to_param(payload) for payload in self.__params.values()]

    def new_param(self, name: str, value: Any = '', type: str = '') -> Param:
        """
        Create a new parameter object.

        Creates an instance of Param with the given name, and optionally the value and data type.
        When the value is not provided then an empty string is assumed.
        If the data type is not defined then "string" is assumed.

        :param name: The parameter name.
        :param value: The parameter value.
        :param type: The data type of the value.

        """

        return Param(name, value=value, type=type, exists=True)

    def has_file(self, name: str) -> bool:
        """
        Check if a file was provided for the action.

        :param name: File name.

        """

        return name in self.__files

    def get_file(self, name: str) -> File:
        """
        Get a file with a given name.

        :param name: File name.

        """

        # TODO: Create the file from the service schema (see PHP SDK and change async too)
        if not self.has_file(name):
            return File(name)

        return payload_to_file(self.__files[name])

    def get_files(self) -> List[File]:
        """Get all action files."""

        return [payload_to_file(payload) for payload in self.__files.values()]

    def new_file(self, name: str, path: str, mime: str = '') -> File:
        """
        Create a new file.

        :param name: File name.
        :param path: File path.
        :param mime: Optional file mime type.

        """

        return File(name, path, mime=mime)

    def set_download(self, file: File) -> Action:
        """
        Set a file as the download.

        :param file: The file object.

        :raises: LookupError

        """

        if not isinstance(file, File):
            raise TypeError('File must be an instance of File class')

        # Check that files server is enabled when the file is a local file
        if file.is_local():
            name = self.get_name()
            version = self.get_version()
            schema = self.get_service_schema(name, version)
            if not schema.has_file_server():
                raise LookupError(f'File server not configured: "{name}" ({version})')

        self._transport.set_download(file)
        return self

    def set_return(self, value: Any) -> Action:
        """
        Set the value to be returned by the action.

        :param value: A value to return.

        :raises: KusanagiError

        """

        if self._schemas:
            name = self.get_name()
            version = self.get_version()
            try:
                # Check that the schema for the current action is available
                schema = self.get_service_schema(name, version)
                action = self.get_action_name()
                action_schema = schema.get_action_schema(action)
                if not action_schema.has_return():
                    raise KusanagiError(f'Cannot set a return value in "{name}" ({version}) for action: "{action}"')

                # Validate that the return value has the type defined in the config
                return_type = action_schema.get_return_type()
                if not isinstance(value, RETURN_TYPES[return_type]):
                    raise KusanagiError(f'Invalid return type given in "{name}" ({version}) for action: "{action}"')
            except LookupError as err:
                # LookupError is raised when the schema for the current service,
                # or for the current action is not available.
                raise KusanagiError(err)
        else:  # pragma: no cover
            # When running the action from the CLI there is no schema available, but the
            # setting of return values must be allowed without restrictions in this case.
            self._logger.warning('Return value set without discovery mapping available')

        self._transport.set_return(value)
        return self

    def set_entity(self, entity: dict) -> Action:
        """
        Set the entity data.

        Sets an object as the entity to be returned by the action.

        Entity is validated when validation is enabled for an entity in the service config file.

        :param entity: The entity object.

        :raises: TypeError

        """

        if not isinstance(entity, dict):
            raise TypeError('Entity must be a dictionary')

        self._transport.add_data(self.get_name(), self.get_version(), self.get_action_name(), entity)
        return self

    def set_collection(self, collection: List[dict]) -> Action:
        """
        Set the collection data.

        Collection is validated when validation is enabled for an entity in the service config file.

        :param collection: The collection list.

        :raises: TypeError

        """

        if not isinstance(collection, list):
            raise TypeError('Collection must be a list')

        for entity in collection:
            if not isinstance(entity, dict):
                raise TypeError('Collection entities must be of type dict')

        self._transport.add_data(self.get_name(), self.get_version(), self.get_action_name(), collection)
        return self

    def relate_one(self, primary_key: str, service: str, foreign_key: str) -> Action:
        """
        Create a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity's primary key and service with the foreign key.

        :param primery_key: The primary key.
        :param service: The foreign service.
        :param foreign_key: The foreign key.

        :raises: ValueError

        """

        if not primary_key:
            raise ValueError('The primary key is empty')

        if not service:
            raise ValueError('The foreign service name is empty')

        if not foreign_key:
            raise ValueError('The foreign key is empty')

        self._transport.add_relate_one(self.get_name(), primary_key, service, foreign_key)
        return self

    def relate_many(self, primary_key: str, service: str, foreign_keys: List[str]) -> Action:
        """
        Create a "one-to-many" relation between entities.

        Creates a "one-to-many" relation between the entity's primary key and service with the foreign keys.

        :param primery_key: The primary key.
        :param service: The foreign service.
        :param foreign_key: The foreign keys.

        :raises: TypeError, ValueError

        """

        if not primary_key:
            raise ValueError('The primary key is empty')

        if not service:
            raise ValueError('The foreign service name is empty')

        if not foreign_keys:
            raise ValueError('The foreign keys are empty')
        elif not isinstance(foreign_keys, list):
            raise TypeError('Foreign keys must be a list')

        self._transport.add_relate_many(self.get_name(), primary_key, service, foreign_keys)
        return self

    def relate_one_remote(self, primary_key: str, address: str, service: str, foreign_key: str) -> Action:
        """
        Creates a "one-to-one" relation between two entities.

        Creates a "one-to-one" relation between the entity's primary key and service with the foreign key.

        This type of relation is done between entities in different realms.

        :param primery_key: The primary key.
        :param address: Foreign service public address.
        :param service: The foreign service.
        :param foreign_key: The foreign key.

        :raises: ValueError

        """

        if not primary_key:
            raise ValueError('The primary key is empty')

        if not address:
            raise ValueError('The foreign service address is empty')

        if not service:
            raise ValueError('The foreign service name is empty')

        if not foreign_key:
            raise ValueError('The foreign key is empty')

        self._transport.add_relate_one_remote(self.get_name(), primary_key, address, service, foreign_key)
        return self

    def relate_many_remote(self, primary_key: str, address: str, service: str, foreign_keys: List[str]) -> Action:
        """
        Create a "one-to-many" relation between entities.

        Creates a "one-to-many" relation between the entity's primary key and service with the foreign keys.

        This type of relation is done between entities in different realms.

        :param primery_key: The primary key.
        :param address: Foreign service public address.
        :param service: The foreign service.
        :param foreign_key: The foreign keys.

        :raises: ValueError, TypeError

        """

        if not primary_key:
            raise ValueError('The primary key is empty')

        if not address:
            raise ValueError('The foreign service address is empty')

        if not service:
            raise ValueError('The foreign service name is empty')

        if not foreign_keys:
            raise ValueError('The foreign keys are empty')
        elif not isinstance(foreign_keys, list):
            raise TypeError('Foreign keys must be a list')

        self._transport.add_relate_many_remote(self.get_name(), primary_key, address, service, foreign_keys)
        return self

    def set_link(self, link: str, uri: str) -> Action:
        """
        Set a link for the given URI.

        :param link: The link name.
        :param uri: The link URI.

        :raises: ValueError

        """

        if not link:
            raise ValueError('The link is empty')

        if not uri:
            raise ValueError('The URI is empty')

        self._transport.add_link(self.get_name(), link, uri)
        return self

    def commit(self, action: str, params: List[Param] = None) -> Action:
        """
        Register a transaction to be called when request succeeds.

        :param action: The action name.
        :param params: Optional list of parameters.

        :raises: ValueError

        """

        if not action:
            raise ValueError('The action name is empty')

        self._transport.add_transaction(
            self._transport.TRANSACTION_COMMIT,
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            action,
            params=params,
        )
        return self

    def rollback(self, action: str, params: List[Param] = None) -> Action:
        """
        Register a transaction to be called when request fails.

        :param action: The action name.
        :param params: Optional list of parameters.

        :raises: ValueError

        """

        if not action:
            raise ValueError('The action name is empty')

        self._transport.add_transaction(
            self._transport.TRANSACTION_ROLLBACK,
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            action,
            params=params,
        )
        return self

    def complete(self, action: str, params: List[Param] = None) -> Action:
        """
        Register a transaction to be called when request finishes.

        This transaction is ALWAYS executed, it doesn't matter if request fails or succeeds.

        :param action: The action name.
        :param params: Optional list of parameters.

        :raises: ValueError

        """

        if not action:
            raise ValueError('The action name is empty')

        self._transport.add_transaction(
            self._transport.TRANSACTION_COMPLETE,
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            action,
            params=params,
        )
        return self

    def call(
        self,
        service: str,
        version: str,
        action: str,
        params: List[Param] = None,
        files: List[File] = None,
        timeout: int = EXECUTION_TIMEOUT,
    ) -> Any:
        """
        Perform a run-time call to a service.

        The result of this call is the return value from the remote action.

        :param service: The service name.
        :param version: The service version.
        :param action: The action name.
        :param params: Optional list of Param objects.
        :param files: Optional list of File objects.
        :param timeout: Optional timeout in milliseconds.

        :raises: ValueError, KusanagiError

        """

        # Check that the call exists in the config
        service_title = f'"{service}" ({version})'
        try:
            schema = self.get_service_schema(self.get_name(), self.get_version())
            action_schema = schema.get_action_schema(self.get_action_name())
            if not action_schema.has_call(service, version, action):
                msg = f'Call not configured, connection to action on {service_title} aborted: "{action}"'
                raise KusanagiError(msg)
        except LookupError as err:
            raise KusanagiError(err)

        # Check that the remote action exists and can return a value, and if it doesn't issue a warning
        try:
            remote_action_schema = self.get_service_schema(service, version).get_action_schema(action)
        except LookupError as err:  # pragma: no cover
            self._logger.warning(err)
        else:
            if not remote_action_schema.has_return():
                raise KusanagiError(f'Cannot return value from {service_title} for action: "{action}"')

        validate_parameter_list(params)
        validate_file_list(files)

        # Check that the file server is enabled when one of the files is local
        if files:
            for file in files:
                if file.is_local():
                    # Stop checking when one local file is found and the file server is enables
                    if schema.has_file_server():
                        break

                    raise KusanagiError(f'File server not configured: {service_title}')

        return_value = None
        transport = None
        client = Client(self._logger, tcp=self._state.values.is_tcp_enabled())
        try:
            # NOTE: The transport set to the call won't have any data added by the action component
            return_value, transport = client.call(
                schema.get_address(),
                self.get_action_name(),
                [service, version, action],
                timeout,
                transport=TransportPayload(self._command.get_transport_data()),  # Use a clean transport for the call
                params=params,
                files=files,
            )
        finally:
            # Always add the call info to the transport, even after an exception is raised during the call
            self._transport.add_call(
                self.get_name(),
                self.get_version(),
                self.get_action_name(),
                service,
                version,
                action,
                client.get_duration(),
                params=params,
                files=files,
                timeout=timeout,
                transport=transport,
            )

        return return_value

    def defer_call(
        self,
        service: str,
        version: str,
        action: str,
        params: List[Param] = None,
        files: List[File] = None,
    ) -> Action:
        """
        Register a deferred call to a service.

        :param service: The service name.
        :param version: The service version.
        :param action: The action name.
        :param params: Optional list of parameters.
        :param files: Optional list of files.

        :raises: ValueError, KusanagiError

        """

        # Check that the deferred call exists in the config
        service_title = f'"{service}" ({version})'
        try:
            schema = self.get_service_schema(self.get_name(), self.get_version())
            action_schema = schema.get_action_schema(self.get_action_name())
            if not action_schema.has_defer_call(service, version, action):
                msg = f'Deferred call not configured, connection to action on {service_title} aborted: "{action}"'
                raise KusanagiError(msg)
        except LookupError as err:
            raise KusanagiError(err)

        # Check that the remote action exists and if it doesn't issue a warning
        try:
            self.get_service_schema(service, version).get_action_schema(action)
        except LookupError as err:  # pragma: no cover
            self._logger.warning(err)

        validate_parameter_list(params)
        validate_file_list(files)

        # Check that the file server is enabled when one of the files is local
        if files:
            for file in files:
                if file.is_local():
                    # Stop checking when one local file is found and the file server is enables
                    if schema.has_file_server():
                        break

                    raise KusanagiError(f'File server not configured: {service_title}')

        self._transport.add_defer_call(
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            service,
            version,
            action,
            params=params,
            files=files,
        )
        return self

    def remote_call(
        self,
        address: str,
        service: str,
        version: str,
        action: str,
        params: List[Param] = None,
        files: List[File] = None,
        timeout: int = EXECUTION_TIMEOUT,
    ) -> Action:
        """
        Register a call to a remote service in another realm.

        These types of calls are done using KTP (KUSANAGI transport protocol).

        :param address: Public address of a gateway from another realm.
        :param service: The service name.
        :param version: The service version.
        :param action: The action name.
        :param params: Optional list of parameters.
        :param files: Optional list of files.
        :param timeout: Optional call timeout in milliseconds.

        :raises: ValueError, KusanagiError

        """

        if not address.startswith('ktp://'):
            raise ValueError(f'The address must start with "ktp://": {address}')

        # Check that the deferred call exists in the config
        service_title = f'[{address}] "{service}" ({version})'
        try:
            schema = self.get_service_schema(self.get_name(), self.get_version())
            action_schema = schema.get_action_schema(self.get_action_name())
            if not action_schema.has_remote_call(address, service, version, action):
                msg = f'Remote call not configured, connection to action on {service_title} aborted: "{action}"'
                raise KusanagiError(msg)
        except LookupError as err:
            raise KusanagiError(err)

        # Check that the remote action exists and if it doesn't issue a warning
        try:
            self.get_service_schema(service, version).get_action_schema(action)
        except LookupError as err:  # pragma: no cover
            self._logger.warning(err)

        validate_parameter_list(params)
        validate_file_list(files)

        # Check that the file server is enabled when one of the files is local
        if files:
            for file in files:
                if file.is_local():
                    # Stop checking when one local file is found and the file server is enables
                    if schema.has_file_server():
                        break

                    raise KusanagiError(f'File server not configured: {service_title}')

        self._transport.add_remote_call(
            address,
            self.get_name(),
            self.get_version(),
            self.get_action_name(),
            service,
            version,
            action,
            params=params,
            files=files,
            timeout=timeout,
        )
        return self

    def error(self, message: str, code: int = 0, status: str = ErrorPayload.DEFAULT_STATUS) -> Action:
        """
        Add an error for the current service.

        Adds an error object to the Transport with the specified message.

        :param message: The error message.
        :param code: The error code.
        :param status: The HTTP status message.

        """

        self._transport.add_error(self.get_name(), self.get_version(), message, code, status)
        return self


class ActionSchema(object):
    """Service action schema."""

    DEFAULT_EXECUTION_TIMEOUT = EXECUTION_TIMEOUT

    def __init__(self, name: str, payload: ActionSchemaPayload):
        """
        Constructor.

        :param name: The name of the service action.
        :param payload: The action schema payload.

        """

        self.__name = name
        self.__payload = payload

    def get_timeout(self) -> int:
        """Get the maximum execution time defined in milliseconds for the action."""

        return self.__payload.get([ns.TIMEOUT], self.DEFAULT_EXECUTION_TIMEOUT)

    def is_deprecated(self) -> bool:
        """Check if action has been deprecated."""

        return self.__payload.get([ns.DEPRECATED], False)

    def is_collection(self) -> bool:
        """Check if the action returns a collection of entities."""

        return self.__payload.get([ns.COLLECTION], False)

    def get_name(self) -> str:
        """Get action name."""

        return self.__name

    def get_entity_path(self) -> str:
        """Get path to the entity."""

        return self.__payload.get([ns.ENTITY_PATH], '')

    def get_path_delimiter(self) -> str:
        """Get delimiter to use for the entity path."""

        return self.__payload.get([ns.PATH_DELIMITER], '/')

    def resolve_entity(self, data: dict) -> dict:
        """
        Get entity from data.

        Get the entity part, based upon the `entity-path` and `path-delimiter`
        properties in the action configuration.

        :param data: The object to get entity from.

        :raises: LookupError

        """

        # The data is traversed only when there is a path, otherwise data is returned as is
        path = self.get_entity_path()
        if path:
            delimiter = self.get_path_delimiter()
            try:
                for name in path.split(delimiter):
                    data = data[name]
            except (TypeError, KeyError):
                raise LookupError(f'Cannot resolve entity for action: {self.get_name()}')

        return data

    def has_entity(self) -> bool:
        """Check if an entity definition exists for the action."""

        return self.__payload.exists([ns.ENTITY])

    def get_entity(self) -> dict:
        """Get the entity definition."""

        return self.__payload.get_entity()

    def has_relations(self) -> bool:
        """Check if any relations exists for the action."""

        return self.__payload.exists([ns.RELATIONS])

    def get_relations(self) -> list:
        """
        Get the relations.

        Each item is an array contains the relation type and the service name.

        """

        return self.__payload.get_relations()

    def get_calls(self) -> list:
        """
        Get service run-time calls.

        Each call item is a list containing the service name, the service version and the action name.

        """

        return self.__payload.get([ns.CALLS], [])

    def has_call(self, name: str, version: str = None, action: str = None) -> bool:
        """
        Check if a run-time call exists for a service.

        :param name: Service name.
        :param version: Optional service version.
        :param action: Optional action name.

        """

        for call in self.get_calls():
            if call[0] not in ('*', name):
                continue

            if version and call[1] not in ('*', version) and not VersionString(version).match(call[1]):
                continue

            if action and call[2] not in ('*', action):
                continue

            # When all given arguments match the call return True
            return True

        # By default call does not exist
        return False

    def has_calls(self) -> bool:
        """Check if any run-time call exists for the action."""

        return self.__payload.exists([ns.CALLS])

    def get_defer_calls(self) -> list:
        """
        Get deferred service calls.

        Each call item is a list containing the service name, the service version and the action name.

        """

        return self.__payload.get([ns.DEFERRED_CALLS], [])

    def has_defer_call(self, name, version: str = None, action: str = None) -> bool:
        """
        Check if a deferred call exists for a service.

        :param name: Service name.
        :param version: Optional service version.
        :param action: Optional action name.

        """

        for call in self.get_defer_calls():
            if call[0] not in ('*', name):
                continue

            if version and call[1] not in ('*', version) and not VersionString(version).match(call[1]):
                continue

            if action and call[2] not in ('*', action):
                continue

            # When all given arguments match the call return True
            return True

        # By default call does not exist
        return False

    def has_defer_calls(self):
        """Check if any deferred call exists for the action."""

        return self.__payload.exists([ns.DEFERRED_CALLS])

    def get_remote_calls(self) -> list:
        """
        Get remote service calls.

        Each remote call item is a list containing the public address of the gateway,
        the service name, the service version and the action name.

        """

        return self.__payload.get([ns.REMOTE_CALLS], [])

    def has_remote_call(self, address: str, name: str = None, version: str = None, action: str = None) -> bool:
        """
        Check if a remote call exists for a service.

        :param address: Gateway address.
        :param name: Optional service name.
        :param version: Optional service version.
        :param action: Optional action name.

        """

        for call in self.get_remote_calls():
            if call[0] not in ('*', address):
                continue

            if name and call[1] not in ('*', name):
                continue

            if version and call[2] not in ('*', version) and not VersionString(version).match(call[2]):
                continue

            if action and call[3] not in ('*', action):
                continue

            # When all given arguments match the call return True
            return True

        # By default call does not exist
        return False

    def has_remote_calls(self) -> bool:
        """Check if any remote call exists for the action."""

        return self.__payload.exists([ns.REMOTE_CALLS])

    def has_return(self) -> bool:
        """Check if a return value is defined for the action."""

        return self.__payload.exists([ns.RETURN])

    def get_return_type(self) -> str:
        """
        Get the data type of the returned action value.

        :raises: ValueError

        """

        if not self.__payload.exists([ns.RETURN, ns.TYPE]):
            raise ValueError(f'Return value not defined for action: {self.get_name()}')

        return self.__payload.get([ns.RETURN, ns.TYPE])

    def get_params(self) -> List[str]:
        """Get the parameter names defined for the action."""

        return self.__payload.get_param_names()

    def has_param(self, name: str) -> bool:
        """
        Check that schema for a parameter exists.

        :param name: A parameter name.

        """

        return name in self.get_params()

    def get_param_schema(self, name: str) -> ParamSchema:
        """
        Get the schema for a parameter.

        :param name: The parameter name.

        :raises: LookupError

        """

        if not self.has_param(name):
            raise LookupError(f'Cannot resolve schema for parameter: {name}')

        return ParamSchema(self.__payload.get_param_schema_payload(name))

    def get_files(self) -> List[str]:
        """Get the file parameter names defined for the action."""

        return self.__payload.get_file_names()

    def has_file(self, name: str) -> bool:
        """
        Check that schema for a file parameter exists.

        :param name: A file parameter name.

        """

        return name in self.get_files()

    def get_file_schema(self, name: str) -> FileSchema:
        """
        Get schema for a file parameter.

        :param name: File parameter name.

        :raises: LookupError

        """

        if not self.has_file(name):
            raise LookupError(f'Cannot resolve schema for file parameter: "{name}"')

        return FileSchema(self.__payload.get_file_schema_payload(name))

    def get_tags(self) -> List[str]:
        """Get the tags defined for the action."""

        return list(self.__payload.get([ns.TAGS], []))

    def has_tag(self, name: str) -> bool:
        """
        Check that a tag is defined for the action.

        The tag name is case sensitive.

        :param name: The tag name.

        """

        return name in self.get_tags()

    def get_http_schema(self) -> HttpActionSchema:
        """Get HTTP action schema."""

        return HttpActionSchema(self.__payload.get_http_action_schema_payload())


class HttpActionSchema(object):
    """HTTP semantics of an action schema in the framework."""

    DEFAULT_METHOD = 'GET'
    DEFAULT_INPUT = 'query'
    DEFAULT_BODY = 'text/plain'

    def __init__(self, payload: HttpActionSchemaPayload):
        """
        Constructor.

        :param payload: The HTTP action schema payload.

        """

        self.__payload = payload

    def is_accessible(self) -> bool:
        """Check if the gateway has access to the action."""

        return self.__payload.get([ns.GATEWAY], True)

    def get_method(self) -> str:
        """Get HTTP method for the action."""

        return self.__payload.get([ns.METHOD], self.DEFAULT_METHOD)

    def get_path(self) -> str:
        """Get URL path for the action."""

        return self.__payload.get([ns.PATH], '')

    def get_input(self) -> str:
        """Get default location of parameters for the action."""

        return self.__payload.get([ns.INPUT], self.DEFAULT_INPUT)

    def get_body(self) -> str:
        """
        Get expected MIME type of the HTTP request body.

        Result may contain a comma separated list of MIME types.

        """

        return ','.join(self.__payload.get([ns.BODY], [self.DEFAULT_BODY]))
