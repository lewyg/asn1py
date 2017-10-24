"""
MyOct ::= OCTET STRING(SIZE(4))
"""
from asn1 import OctetString


class MyOct(OctetString):
    size = 4

    def check_constraints(self, value):
        result = len(value) == 4

        return result
