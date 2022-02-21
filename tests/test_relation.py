# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2022 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.


class test_relation():
    from kusanagi.sdk import ForeignRelation
    from kusanagi.sdk import Relation

    fks = {
        '1.2.3.4:77': {
            'bar': ['1', '2'],
        },
        '1.2.3.4:8080': {
            'baz': '1',
        },
    }
    relation = Relation('1.2.3.4:77', 'foo', '1', fks)
    assert relation.get_address() == '1.2.3.4:77'
    assert relation.get_name() == 'foo'
    assert relation.get_primary_key() == '1'

    foreign_relations = relation.get_foreign_relations()
    assert isinstance(foreign_relations, list)
    assert len(foreign_relations) == 2

    foreign_many, foreign_one = foreign_relations
    assert isinstance(foreign_many, ForeignRelation)
    assert foreign_many.get_type() == ForeignRelation.TYPE_MANY
    assert foreign_many.get_foreign_keys() == ['1', '2']
    assert isinstance(foreign_one, ForeignRelation)
    assert foreign_one.get_type() == ForeignRelation.TYPE_ONE
    assert foreign_one.get_foreign_keys() == ['1']
