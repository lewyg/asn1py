"""
MyBit ::= BIT STRING(SIZE(20))
"""
from asn1 import BitString


class MyBit(BitString):
    def init_value(self):
        return '000'

    def check_constraints(self, value):
        result = len(value) == 3

        return result
