"""
MyBit ::= BIT STRING(SIZE(20))
"""
from asn1 import BitString


class MyBit(BitString):
    def check_constraints(self, value):
        result = len(value) == 20

        return result
