"""
MyBit ::= BIT STRING(SIZE(20))
"""
from asn1 import BitString


class MyBit(BitString):
    size = 20

    def check_constraints(self, value):
        bytes_size = self._get_bytes_size_from_bits(20)

        result = len(value) == bytes_size

        return result
