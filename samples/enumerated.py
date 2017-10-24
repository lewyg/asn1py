"""
MyEnum ::= ENUMERATED{
    alpha, beta, gamma
}
"""
from asn1 import Enumerated


class MyEnum(Enumerated):
    NONE = None
    alpha = 1
    beta = 2
    gamma = 3
