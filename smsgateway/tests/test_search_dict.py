from __future__ import unicode_literals

from pytest import mark

from smsgateway.search_dict import SearchDict


@mark.parametrize('input_dict,key,result', (
    ({'key': 'value'}, 'key', 'value'),
    ({'key': 'value'}, 'otherkey', ''),
    ({'key': None}, 'key', ''),
    ({'key': ['value']}, 'key', ['value']),
    ({'key': [{'otherkey': 'value'}]}, 'otherkey', 'value'),
))
def test_find(input_dict, key, result):
    assert SearchDict(input_dict).find(key) == result


@mark.parametrize('value', ('value', ['value']))
def test_find_as_list(value):
    assert SearchDict({'key': value}).find('key', as_list=True) == ['value']
