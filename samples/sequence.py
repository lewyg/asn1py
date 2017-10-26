"""
MyStruct ::= SEQUENCE {
    a INTEGER (1..10),
    b REAL OPTIONAL,
    c MyEnum OPTIONAL
}
"""
from asn1 import Sequence, Integer
from samples.enumerated import MyEnum


class MyStruct_a(Integer):
    def check_constraints(self, value):
        result = 1 <= value <= 10

        return result


class MyStruct(Sequence):
    def __init__(self):
        self.a = MyStruct_a()
        self.b = Integer()
        self.c = MyEnum.NONE

        self.exists = dict(
            b=True,
            c=True,
        )
