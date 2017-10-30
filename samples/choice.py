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
        self.alpha = MyStruct()  # type: MyStruct.__checktype__
        self.beta = Integer()  # type: Integer.__checktype__
        self.octStr = MyChoice_octStr()  # type: MyChoice_octStr.__checktype__

        self.attributes = dict(
            alpha=False,
            beta=False,
            octStr=False
        )

        self.initialized = True
