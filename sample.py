# ASN.1 Data model

import asn1

MAX = asn1.INT_MAX
MIN = asn1.INT_MIN
INF = asn1.INFINITY
NAN = asn1.NAN


def get_string_init_char(obj):
    if isinstance(obj, asn1.NumericString) or isinstance(obj, asn1.BitString):
        return '0'
    elif isinstance(obj, asn1.OctetString):
        return b'0'
    else:
        return ' '


class MyBool(asn1.Boolean):
    pass


class MyNull(asn1.Null):
    pass


class MyInt(asn1.Integer):
    constraints = 'SIZE(0 .. 100)'

    def init_value(self):
        return 0

    def check_constraints(self, value):
        result = 0 <= value <= 100
        return result


class MyInt2(asn1.Integer):
    constraints = 'SIZE(1 .. 3)'

    def init_value(self):
        return 1

    def check_constraints(self, value):
        result = 1 <= value <= 3
        return result


class MyStr(asn1.IA5String):
    constraints = 'SIZE(1 .. 10)'

    def init_value(self):
        return get_string_init_char(self) * 1

    def check_constraints(self, value):
        result = 1 <= len(value) <= 10
        return result


class MyNumStr(asn1.NumericString):
    constraints = 'SIZE(3)'

    def init_value(self):
        return get_string_init_char(self) * 3

    def check_constraints(self, value):
        result = len(value) == 3
        return result


class MyBit(asn1.BitString):
    constraints = 'SIZE(16)'

    def init_value(self):
        return get_string_init_char(self) * 16

    def check_constraints(self, value):
        result = len(value) == 16
        return result


class MyOct(asn1.OctetString):
    constraints = 'SIZE(3 .. 8)'

    def init_value(self):
        return get_string_init_char(self) * 3

    def check_constraints(self, value):
        result = 3 <= len(value) <= 8
        return result


class MyReal(asn1.Real):
    constraints = 'SIZE(1.00000000000000000000E+001 .. 2.60000000000000000000E+001)'

    def init_value(self):
        return 1.00000000000000000000E+001

    def check_constraints(self, value):
        result = 1.00000000000000000000E+001 <= value <= 2.60000000000000000000E+001
        return result


class MyEnum(asn1.Enumerated):
    class Value(asn1.Enumerated.Value):
        NONE = None
        alpha = 0
        beta = 1
        gamma = 2

    __base__ = Value

# for global access
alpha = 0
beta = 1
gamma = 2


class MyPDU(asn1.Sequence):
    def __init__(self, **kwargs):
        self.attributes = dict()

        # a
        class _aType(asn1.Integer):
            constraints = 'SIZE(MIN .. MAX)'

            def init_value(self):
                return MIN

            def check_constraints(self, value):
                result = MIN <= value <= MAX
                return result

        self.aType = _aType
        self.a: self.aType.__typing__ = self.aType()
        self.attributes['a'] = True

        # b
        class _bType(asn1.Null):
            pass

        self.bType = _bType
        self.b: self.bType.__typing__ = self.bType()
        self.attributes['b'] = True

        # c
        class _cType(asn1.NumericString):
            constraints = 'SIZE(2)'

            def init_value(self):
                return get_string_init_char(self) * 2

            def check_constraints(self, value):
                result = len(value) == 2
                return result

        self.cType = _cType
        self.c: self.cType.__typing__ = self.cType()
        self.attributes['c'] = True

        self.initialized = True
        self._create_from_kwargs(kwargs)


class MyStruct(asn1.Sequence):
    def __init__(self, **kwargs):
        self.attributes = dict()

        # a
        class _aType(asn1.Integer):
            constraints = 'SIZE(1 .. 10)'

            def init_value(self):
                return 1

            def check_constraints(self, value):
                result = 1 <= value <= 10
                return result

        self.aType = _aType
        self.a: self.aType.__typing__ = self.aType()
        self.attributes['a'] = True

        # b
        class _bType(asn1.Real):
            constraints = 'SIZE(MIN .. MAX)'

            def init_value(self):
                return MIN

            def check_constraints(self, value):
                result = MIN <= value <= MAX
                return result

        self.bType = _bType
        self.b: self.bType.__typing__ = self.bType()
        self.attributes['b'] = True

        # c
        class _cType(MyEnum):
            pass

        self.cType = _cType
        self.c: self.cType.__typing__ = self.cType()
        self.attributes['c'] = True

        self.initialized = True
        self._create_from_kwargs(kwargs)


class MyChoice(asn1.Choice):
    def __init__(self, choice):
        self.attributes = dict()

        # alpha
        class _alphaType(MyStruct):
            pass

        self.alphaType = _alphaType
        self.alpha: self.alphaType.__typing__ = self.alphaType()
        self.attributes['alpha'] = False

        # beta
        class _betaType(asn1.Integer):
            constraints = 'SIZE(MIN .. MAX)'

            def init_value(self):
                return MIN

            def check_constraints(self, value):
                result = MIN <= value <= MAX
                return result

        self.betaType = _betaType
        self.beta: self.betaType.__typing__ = self.betaType()
        self.attributes['beta'] = False

        # octStr
        class _octStrType(asn1.OctetString):
            constraints = 'SIZE(4)'

            def init_value(self):
                return get_string_init_char(self) * 4

            def check_constraints(self, value):
                result = len(value) == 4
                return result

        self.octStrType = _octStrType
        self.octStr: self.octStrType.__typing__ = self.octStrType()
        self.attributes['octStr'] = False

        self.initialized = True
        self._append_choice(choice)


class MySqOf(asn1.SequenceOf):
    class _ElementType(asn1.Sequence):
        def __init__(self, **kwargs):
            self.attributes = dict()

            # a2
            class _a2Type(asn1.Integer):
                constraints = 'SIZE(1 .. 10)'

                def init_value(self):
                    return 1

                def check_constraints(self, value):
                    result = 1 <= value <= 10
                    return result

            self.a2Type = _a2Type
            self.a2: self.a2Type.__typing__ = self.a2Type()
            self.attributes['a2'] = True

            # b2
            class _b2Type(asn1.Real):
                constraints = 'SIZE(MIN .. MAX)'

                def init_value(self):
                    return MIN

                def check_constraints(self, value):
                    result = MIN <= value <= MAX
                    return result

            self.b2Type = _b2Type
            self.b2: self.b2Type.__typing__ = self.b2Type()
            self.attributes['b2'] = True

            # c2
            class _c2Type(asn1.Integer):
                constraints = 'SIZE(MIN .. MAX)'

                def init_value(self):
                    return MIN

                def check_constraints(self, value):
                    result = MIN <= value <= MAX
                    return result

            self.c2Type = _c2Type
            self.c2: self.c2Type.__typing__ = self.c2Type()
            self.attributes['c2'] = True

            self.initialized = True
            self._create_from_kwargs(kwargs)

    __element__ = _ElementType

    constraints = 'SIZE(1 .. 25)'

    def init_value(self):
        return 1  # array size

    def check_constraints(self, value):
        result = 1 <= len(value) <= 25
        return result


class TypeEnumerated(asn1.Enumerated):
    class Value(asn1.Enumerated.Value):
        NONE = None
        red = 0
        green = 1
        blue = 2

    __base__ = Value

# for global access
red = 0
green = 1
blue = 2


class My2ndEnumerated(TypeEnumerated):
    pass


class AComplexMessage(asn1.Sequence):
    def __init__(self, **kwargs):
        self.attributes = dict()

        # intVal
        class _intValType(asn1.Integer):
            constraints = 'SIZE(0 .. 10)'

            def init_value(self):
                return 0

            def check_constraints(self, value):
                result = 0 <= value <= 10
                return result

        self.intValType = _intValType
        self.intVal: self.intValType.__typing__ = self.intValType()
        self.attributes['intVal'] = True

        # int2Val
        class _int2ValType(asn1.Integer):
            constraints = 'SIZE(-10 .. 10)'

            def init_value(self):
                return -10

            def check_constraints(self, value):
                result = -10 <= value <= 10
                return result

        self.int2ValType = _int2ValType
        self.int2Val: self.int2ValType.__typing__ = self.int2ValType()
        self.attributes['int2Val'] = True

        # int3Val
        class _int3ValType(MyInt):
            pass

        self.int3ValType = _int3ValType
        self.int3Val: self.int3ValType.__typing__ = self.int3ValType()
        self.attributes['int3Val'] = True

        # strVal
        class _strValType(MyStr):
            pass

        self.strValType = _strValType
        self.strVal: self.strValType.__typing__ = self.strValType()
        self.attributes['strVal'] = True

        # intArray
        class _intArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Integer):
                constraints = 'SIZE(0 .. 3)'

                def init_value(self):
                    return 0

                def check_constraints(self, value):
                    result = 0 <= value <= 3
                    return result

            __element__ = _ElementType

            constraints = 'SIZE(10 .. 10)'

            def init_value(self):
                return 10  # array size

            def check_constraints(self, value):
                result = 10 <= len(value) <= 10
                return result

        self.intArrayType = _intArrayType
        self.intArray: self.intArrayType.__typing__ = self.intArrayType()
        self.attributes['intArray'] = True

        # realArray
        class _realArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Real):
                constraints = 'SIZE(1.00000000000000010000E-001 .. 3.14000000000000010000E+000)'

                def init_value(self):
                    return 1.00000000000000010000E-001

                def check_constraints(self, value):
                    result = 1.00000000000000010000E-001 <= value <= 3.14000000000000010000E+000
                    return result

            __element__ = _ElementType

            constraints = 'SIZE(15 .. 15)'

            def init_value(self):
                return 15  # array size

            def check_constraints(self, value):
                result = 15 <= len(value) <= 15
                return result

        self.realArrayType = _realArrayType
        self.realArray: self.realArrayType.__typing__ = self.realArrayType()
        self.attributes['realArray'] = True

        # octStrArray
        class _octStrArrayType(asn1.SequenceOf):
            class _ElementType(asn1.OctetString):
                constraints = 'SIZE(1 .. 10)'

                def init_value(self):
                    return get_string_init_char(self) * 1

                def check_constraints(self, value):
                    result = 1 <= len(value) <= 10
                    return result

            __element__ = _ElementType

            constraints = 'SIZE(20 .. 20)'

            def init_value(self):
                return 20  # array size

            def check_constraints(self, value):
                result = 20 <= len(value) <= 20
                return result

        self.octStrArrayType = _octStrArrayType
        self.octStrArray: self.octStrArrayType.__typing__ = self.octStrArrayType()
        self.attributes['octStrArray'] = True

        # enumArray
        class _enumArrayType(asn1.SequenceOf):
            class _ElementType(TypeEnumerated):
                pass

            __element__ = _ElementType

            constraints = 'SIZE(12 .. 12)'

            def init_value(self):
                return 12  # array size

            def check_constraints(self, value):
                result = 12 <= len(value) <= 12
                return result

        self.enumArrayType = _enumArrayType
        self.enumArray: self.enumArrayType.__typing__ = self.enumArrayType()
        self.attributes['enumArray'] = True

        # enumValue
        class _enumValueType(TypeEnumerated):
            pass

        self.enumValueType = _enumValueType
        self.enumValue: self.enumValueType.__typing__ = self.enumValueType()
        self.attributes['enumValue'] = True

        # enumValue2
        class _enumValue2Type(asn1.Enumerated):
            class Value(asn1.Enumerated.Value):
                NONE = None
                truism = 0
                falsism = 1

            __base__ = Value

        # for global access
        truism = 0
        falsism = 1

        self.enumValue2Type = _enumValue2Type
        self.enumValue2: self.enumValue2Type.__typing__ = self.enumValue2Type()
        self.attributes['enumValue2'] = True

        # label
        class _labelType(asn1.OctetString):
            constraints = 'SIZE(10 .. 40)'

            def init_value(self):
                return get_string_init_char(self) * 10

            def check_constraints(self, value):
                result = 10 <= len(value) <= 40
                return result

        self.labelType = _labelType
        self.label: self.labelType.__typing__ = self.labelType()
        self.attributes['label'] = True

        # bAlpha
        class _bAlphaType(asn1.Boolean):
            pass

        self.bAlphaType = _bAlphaType
        self.bAlpha: self.bAlphaType.__typing__ = self.bAlphaType()
        self.attributes['bAlpha'] = True

        # bBeta
        class _bBetaType(asn1.Boolean):
            pass

        self.bBetaType = _bBetaType
        self.bBeta: self.bBetaType.__typing__ = self.bBetaType()
        self.attributes['bBeta'] = True

        self.initialized = True
        self._create_from_kwargs(kwargs)


# xxx
class _xxxType(asn1.Integer):
    constraints = 'SIZE(5 .. 20)'

    def init_value(self):
        return 5

    def check_constraints(self, value):
        result = 5 <= value <= 20
        return result


xxx: _xxxType.__typing__ = _xxxType(13)


# vMyBool
class _vMyBoolType(MyBool):
    pass


vMyBool: _vMyBoolType.__typing__ = _vMyBoolType(True)


# vMyInt
class _vMyIntType(MyInt):
    pass


vMyInt: _vMyIntType.__typing__ = _vMyIntType(88)


# v2MyInt
class _v2MyIntType(MyInt):
    pass


v2MyInt: _v2MyIntType.__typing__ = _v2MyIntType(vMyInt)


# vMyStr
class _vMyStrType(MyStr):
    pass


vMyStr: _vMyStrType.__typing__ = _vMyStrType("AAABBC")


# vMyNumStr
class _vMyNumStrType(MyNumStr):
    pass


vMyNumStr: _vMyNumStrType.__typing__ = _vMyNumStrType("123")


# vMyBit
class _vMyBitType(MyBit):
    pass


vMyBit: _vMyBitType.__typing__ = _vMyBitType(bytes.fromhex('FFAC'))


# vMyOct
class _vMyOctType(MyOct):
    pass


vMyOct: _vMyOctType.__typing__ = _vMyOctType(bytes.fromhex('12345678'))


# vMyReal
class _vMyRealType(MyReal):
    pass


vMyReal: _vMyRealType.__typing__ = _vMyRealType(1.71230000000000010000E+001)


# vMyEnum
class _vMyEnumType(MyEnum):
    pass


vMyEnum: _vMyEnumType.__typing__ = _vMyEnumType(alpha)


# pdu1
class _pdu1Type(MyPDU):
    pass


pdu1: _pdu1Type.__typing__ = _pdu1Type(a=1, b=None, c="42")


# vMyStruct
class _vMyStructType(MyStruct):
    pass


vMyStruct: _vMyStructType.__typing__ = _vMyStructType(a=2, c=alpha)


# vMyChoice
class _vMyChoiceType(MyChoice):
    pass


vMyChoice: _vMyChoiceType.__typing__ = _vMyChoiceType(choice=dict(name='alpha', value=dict(a=2, c=alpha)))


# End
