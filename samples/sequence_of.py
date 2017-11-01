"""
ASNSamples DEFINITIONS AUTOMATIC TAGS ::= BEGIN

MySqOf ::= SEQUENCE (SIZE(1..20|25)) OF SEQUENCE {
  a2 INTEGER (1..10),
  b2 REAL OPTIONAL,
  c2 INTEGER OPTIONAL
}

END
"""
from asn1 import SequenceOf, Real, Integer, Sequence


class MySqOfElement_a(Integer):
    constraints = '1..10'

    def init_value(self):
        return 1

    def check_constraints(self, value):
        result = 1 <= value <= 10

        return result


class MySqOfElement(Sequence):
    def __init__(self):
        self.a: MySqOfElement_a.__typing__ = MySqOfElement_a()
        self.b: Real.__typing__ = Real()
        self.c: Integer.__typing__ = Integer()

        self.attributes = dict(
            a=True,
            b=True,
            c=True,
        )

        self.initialized = True


class MySqOf(SequenceOf):
    __size__ = 25
    __element__ = MySqOfElement

    constraints = 'SIZE(1..20|25)'

    def check_constraints(self, value):
        result = 1 <= len(value) <= 20
        result = result or len(value) == 25

        return result
