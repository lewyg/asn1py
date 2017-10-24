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
    def check_constraints(self, value):
        result = 1 <= value <= 10

        return result


class MySqOfElement(Sequence):
    def __init__(self):
        self.a = MySqOfElement_a()
        self.b = Real()
        self.c = Integer()

        self.exists = dict(
            b=True,
            c=True,
        )


class MySqOf(SequenceOf):
    size = 25
    kind = MySqOfElement

    def check_constraints(self, value):
        result = 1 <= len(value) <= 20
        result = result or len(value) == 25

        return result
