"""
MyInt ::= INTEGER(1|2|3)
"""
from asn1 import Integer


class MyInt(Integer):
    def init_value(self):
        return 1

    def check_constraints(self, value):
        result = value == 1
        result = result or value == 2
        result = result or value == 3

        return result
