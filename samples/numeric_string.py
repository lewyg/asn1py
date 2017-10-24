"""
MyNumString ::= NUMERIC STRING(SIZE(3))
"""
from asn1 import NumericString


class MyNumString(NumericString):
    size = 3

    def check_constraints(self, value):
        result = len(value) == 3

        return result
