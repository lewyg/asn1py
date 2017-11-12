"""
MyEnum ::= ENUMERATED{
    alpha, beta, gamma
}
"""
from asn1 import Enumerated


class MyEnum(Enumerated):
    class Value(Enumerated.Value):
        NONE = None
        alpha = 1
        beta = 2
        gamma = 3

    __simple__ = Value
