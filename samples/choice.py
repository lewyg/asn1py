"""
MyChoice ::= CHOICE {
    alpha MyStruct,
    beta Integer,
    octStr OCTET STRING(SIZE(4))
}
"""
from asn1 import OctetString, Choice, Integer
from samples.sequence import MyStruct


class MyChoice_octStr(OctetString):
    def init_value(self):
        return b'\x00\x00\x00\x00'

    def check_constraints(self, value):
        result = len(value) == 4

        return result


class MyChoice(Choice):
    def __init__(self):
        self.alpha: MyStruct.__checktype__ = MyStruct()
        self.beta: Integer.__checktype__ = Integer()
        self.octStr: MyChoice_octStr.__checktype__ = MyChoice_octStr()

        self.attributes = dict(
            alpha=False,
            beta=False,
            octStr=False
        )

        self.initialized = True
