"""
MyReal ::= REAL(10.0..20.0|25.0..26.0)
"""
from asn1 import Real


class MyReal(Real):
    def check_constraints(self, value):
        result = 10.0 <= value <= 20.0
        result = result or 25.0 <= value <= 26.0

        return result
