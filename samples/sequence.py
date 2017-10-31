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
    def init_value(self):
        return 1

    def check_constraints(self, value):
        result = 1 <= value <= 10

        return result


class MyStruct(Sequence):
    def __init__(self):
        self.a: MyStruct_a._checktype_ = MyStruct_a()
        self.b: Integer._checktype_ = Integer()
        self.c: MyEnum._checktype_ = MyEnum()

        self.attributes = dict(
            a=True,
            b=True,
            c=True,
        )

        self.initialized = True
