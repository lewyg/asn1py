"""
MyBit ::= BIT STRING(SIZE(20))
"""
from asn1 import BitString, Sequence, NumericString


class MyBit(BitString):
    def check_constraints(self, value):
        result = len(value) == 3

        return result

class A(Sequence):
    def __init__(self):
        self.x = MyBit()

        self.attributes = {'x':True}

        self.initialized = True

a = A()

a.x = '101'
print(a.x[:1])

x = '123'
x[2] = '4'
print(x[2])

print(a.x, type(a.x))