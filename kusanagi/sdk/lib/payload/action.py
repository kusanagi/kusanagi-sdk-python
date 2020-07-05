# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import List

from . import Payload
from . import ns
from .file import FileSchemaPayload
from .param import ParamSchemaPayload
from ..datatypes import TYPE_STRING


def payload_to_entity(payload: dict, entity: dict = None) -> dict:
    """
    Create a new entity definition object from a payload.

    :param payload: Entity definition payload.
    :param entity: An optional entity to update with the definition values.

    """

    if entity is None:
        entity = {}

    if not payload:
        return entity

    # Add validate field only to top level entity
    if not entity:
        entity['validate'] = payload.get(ns.VALIDATE, False)

    # Add fields to entity
    if ns.FIELD in payload:
        entity['field'] = []
        for field in payload[ns.FIELD]:
            entity['field'].append({
                'name': field.get(ns.NAME),
                'type': field.get(ns.TYPE, TYPE_STRING),
                'optional': field.get(ns.OPTIONAL, False),
            })

    # Add field sets to entity
    if ns.FIELDS in payload:
        entity['fields'] = []
        for fields in payload[ns.FIELDS]:
            fieldset = {
                'name': fields.get(ns.NAME),
                'optional': fields.get(ns.OPTIONAL, False),
            }

            # Add inner field and fieldsets
            if ns.FIELD in fields or ns.FIELDS in fields:
                fieldset = payload_to_entity(fields, fieldset)

            entity['fields'].append(fieldset)

    return entity


class ActionSchemaPayload(Payload):
    """Handles operation on action schema payloads."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__params = self.get([ns.PARAMS], {})
        self.__files = self.get([ns.FILES], {})

    def get_entity(self) -> dict:
        """Get the entity definition as an object."""

        payload = self.get([ns.ENTITY])
        return payload_to_entity(payload)

    def get_relations(self) -> list:
        """Get the relations."""

        return [
            [payload.get(ns.TYPE, 'one'), payload.get(ns.NAME)]
            for payload in self.get([ns.RELATIONS], [])
        ]

    def get_param_names(self) -> List[str]:
        """Get the list of all the action parameters."""

        return list(self.__params.keys())

    def get_param_schema_payload(self, name: str) -> ParamSchemaPayload:
        """
        Get the schema for a parameter.

        :param name: The parameter name.

        :raises: KeyError

        """

        return ParamSchemaPayload(name, self.__params[name])

    def get_file_names(self) -> List[str]:
        """Get the list of all the action file parameters."""

        return list(self.__files.keys())

    def get_file_schema_payload(self, name: str) -> FileSchemaPayload:
        """
        Get the schema for a file parameter.

        :param name: The file parameter name.

        :raises: KeyError

        """

        return FileSchemaPayload(name, self.__files[name])

    def get_http_action_schema_payload(self) -> 'HttpActionSchemaPayload':
        """Get the HTTP schema for the action."""

        return HttpActionSchemaPayload(self.get([ns.HTTP], {}))


class HttpActionSchemaPayload(Payload):
    """Handles operation on HTTP action schema payloads."""
