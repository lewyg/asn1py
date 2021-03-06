"""
MyReal ::= REAL(10.0..20.0|25.0..26.0)
"""
from asn1 import Real


class MyReal(Real):
    constraints = '10.0..20.0|25.0..26.0'

    def init_value(self):
        return 10.0

    def check_constraints(self, value):
        result = 10.0 <= value <= 20.0
        result = result or 25.0 <= value <= 26.0

        return result
