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
    constraints = '1..10'

    def init_value(self):
        return 1

    def check_constraints(self, value):
        result = 1 <= value <= 10

        return result


class MyStruct(Sequence):
    def __init__(self):
        self.a: MyStruct_a.__typing__ = MyStruct_a()
        self.b: Integer.__typing__ = Integer()
        self.c: MyEnum.__typing__ = MyEnum()

        self.attributes = dict(
            a=True,
            b=True,
            c=True,
        )

        self.initialized = True
