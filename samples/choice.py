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
    max_size = 4

    def check_constraints(self, value):
        result = len(value) == 4

        return result


class MyChoice(Choice):
    def __init__(self):
        self.alpha = MyStruct()
        self.beta = Integer()
        self.octStr = MyChoice_octStr()

        self.exists = dict(
            alpha=False,
            beta=False,
            octStr=False
        )
