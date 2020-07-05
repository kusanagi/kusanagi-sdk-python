# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2020 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from typing import List
from typing import Union


class BaseRelation(object):
    """Base class for service relations."""

    def __init__(self, address: str, name: str):
        """
        Constructor.

        :param address: A gateway network address.
        :param name: The name of the service.

        """

        self.__address = address
        self.__name = name

    def get_address(self) -> str:
        """Get the network address of the gateway."""

        return self.__address

    def get_name(self) -> str:
        """Get the name of the service."""

        return self.__name


class Relation(BaseRelation):
    """Relation between two services."""

    def __init__(self, address: str, name: str, primary_key: str, foreign_relations: dict):
        """
        Constructor.

        The foreign relations is a dict where each key is the address of the remote gateway
        and each of the values is another dict containing remote service names as keys and
        foreign keys as values, where foreign keys is a single value or a list of values.

        :param address: A gateway network address.
        :param name: The name of the service.
        :param primary_key: The primary key of the local service entity.
        :param foreign_relations: The foreign relations.

        """

        super().__init__(address, name)
        self.__primary_key = primary_key
        self.__foreign_relations = foreign_relations

    def get_primary_key(self) -> str:
        """Get the primary key of the local service entity."""

        return self.__primary_key

    def get_foreign_relations(self) -> List['ForeignRelation']:
        """Get the foreign service relations."""

        relations = []
        # Get the remote gateway address and the foreign relations
        for address, services in self.__foreign_relations.items():
            # Each relation belongs to a service in the remote gateway
            for name, foreign_keys in services.items():
                relations.append(ForeignRelation(address, name, foreign_keys))

        return relations


class ForeignRelation(BaseRelation):
    """Foreign relation between two services."""

    TYPE_ONE = 'one'
    TYPE_MANY = 'many'

    def __init__(self, address: str, name: str, foreign_keys: Union[str, List[str]]):
        """
        Constructor.

        :param address: A remote gateway network address.
        :param name: The name of the remote service.
        :param foreign_keys: The foreign keys.

        """

        super().__init__(address, name)
        self.__foreign_keys = foreign_keys

    def get_type(self) -> str:
        """
        Get the type of the relation.

        The relation type can be either "one" or "many".

        """

        return self.TYPE_MANY if isinstance(self.__foreign_keys, list) else self.TYPE_ONE

    def get_foreign_keys(self) -> List[str]:
        """Get the foreign key values for the relation."""

        return [self.__foreign_keys] if self.get_type() == self.TYPE_ONE else list(self.__foreign_keys)
