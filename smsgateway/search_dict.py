from __future__ import unicode_literals

from builtins import str
from collections import OrderedDict
from re import compile, escape


class SearchDict(OrderedDict):
    """
    Helper class to parse SOAP results to. It can be used by calling .find('x') to find the element with key x.

    Kindly borrowed from silent IMSI migration tool.
    """
    def match(self, pattern):
        regex = compile('^' + escape(pattern) + '$')

        def helper(dct):
            for key, value in dct.items():
                if isinstance(value, dict):
                    for pair in helper(value):
                        yield pair
                elif isinstance(value, list):
                    for elem in value:
                        if isinstance(elem, dict):
                            for pair in helper(elem):
                                yield pair
                if isinstance(key, str) and regex.search(key):
                    yield key, value

        return helper(self)

    def find(self, pattern, as_list=False):
        try:
            _, value = next(self.match(pattern))
            if value is None:
                value = ''
        except StopIteration:
            return [] if as_list else ''
        else:
            if isinstance(value, (tuple, list)):
                return list(value)
            else:
                return [value] if as_list else value
