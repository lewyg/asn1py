"""
MyStruct ::= SEQUENCE {
    a INTEGER (1..10),
    b REAL OPTIONAL,
    c MyEnum OPTIONAL
}
"""
from asn1 import Sequence, Integer, Real
from samples.enumerated import MyEnum


class MyStruct_a(Integer):
    constraints = '1..10'

    @classmethod
    def init_value(cls):
        return 1

    @classmethod
    def check_constraints(cls, value):
        result = 1 <= value <= 10

        return result


class MyStruct(Sequence):
    @property
    def a(self):
        return self._a.get()

    @a.setter
    def a(self, value):
        self._a.set(value)

    @property
    def b(self):
        return self._b.get()

    @b.setter
    def b(self, value):
        self._b.set(value)

    @property
    def c(self):
        return self._c.get()

    @c.setter
    def c(self, value):
        self._c.set(value)

    def __init__(self, source):
        self._a = MyStruct_a()
        self._b = Real()
        self._c = MyEnum()

        self.attributes = dict(
            a=True,
            b=True,
            c=True,
        )
        self.optionals = ['c']

        self.initialized = True
        self._init_sequence(source)


x = MyStruct({'a': 8, 'b': 5.5})
x.c = 3
print(x)
