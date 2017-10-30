"""
MyOct ::= OCTET STRING(SIZE(4))
"""
from asn1 import OctetString


class MyOct(OctetString):
    def init_value(self):
        return b'\x00\x00\x00\x00'

    def check_constraints(self, value):
        result = len(value) == 4

        return result
