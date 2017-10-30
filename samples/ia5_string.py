"""
MyString ::= IA5String(SIZE(1..10))(FROM("A".."Z"|"abcde"))
"""
from asn1 import IA5String


class MyString(IA5String):
    def init_value(self):
        return 'A'

    def check_constraints(self, value):
        result = 1 <= len(value) <= 10
        result = result and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcd" for c in value)

        return result
