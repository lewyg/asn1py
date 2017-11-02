"""
Frame-Types DEFINITIONS ::= BEGIN
    MyInt ::= INTEGER (0..2359296)
    frameMaxBytes MyInt ::= 235929
    MySeq ::= OCTET STRING (SIZE(0..frameMaxBytes))
END
"""
from asn1 import Integer, OctetString


class MyInt(Integer):
    constraints = '(0..2359296)'

    def init_value(self):
        return 0

    def check_constraints(self, value):
        result = 0 <= value <= 235929

        return result


class MySeq(OctetString):
    constraints = 'SIZE(0..frameMaxBytes)'

    def init_value(self):
        return b'\x00'

    def check_constraints(self, value):
        result = 0 <= len(value) <= 235929

        return result


frameMaxBytes = MyInt(235929)
