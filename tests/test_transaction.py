# Python 3 SDK for the KUSANAGI(tm) framework (http://kusanagi.io)
# Copyright (c) 2016-2021 KUSANAGI S.L. All rights reserved.
#
# Distributed under the MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
import pytest


def test_transaction_defaults():
    from kusanagi.sdk import Transaction

    transaction = Transaction(Transaction.TYPE_COMMIT, {})
    assert transaction.get_type() == Transaction.TYPE_COMMIT
    assert transaction.get_name() == ''
    assert transaction.get_version() == ''
    assert transaction.get_caller_action() == ''
    assert transaction.get_callee_action() == ''
    assert transaction.get_params() == []


def test_transaction():
    from kusanagi.sdk import Param
    from kusanagi.sdk import Transaction
    from kusanagi.sdk.lib.payload import ns

    transaction = Transaction(Transaction.TYPE_COMPLETE, {
        ns.NAME: 'foo',
        ns.VERSION: '1.0.1',
        ns.ACTION: 'bar',
        ns.CALLER: 'baz',
        ns.PARAMS: [{
            ns.NAME: 'blah',
        }],
    })
    assert transaction.get_type() == Transaction.TYPE_COMPLETE
    assert transaction.get_name() == 'foo'
    assert transaction.get_version() == '1.0.1'
    assert transaction.get_callee_action() == 'bar'
    assert transaction.get_caller_action() == 'baz'
    params = transaction.get_params()
    assert isinstance(params, list)
    assert len(params) == 1
    param = params[0]
    assert isinstance(param, Param)
    assert param.get_name() == 'blah'


def test_transaction_invalid_type():
    from kusanagi.sdk import Transaction

    with pytest.raises(TypeError):
        Transaction('invalid', {})
