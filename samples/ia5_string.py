"""
MyString ::= IA5String(SIZE(1..10))(FROM("A".."Z"|"abcde"))
"""
from asn1 import IA5String


class MyString(IA5String):
    max_size = 10

    def check_constraints(self, value):
        result = all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcd" for c in value)

        return result
