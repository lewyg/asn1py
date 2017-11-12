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


def add_globals(**kwargs):
    for name, value in kwargs.items():
        globals()[name] = value


class MyBool(asn1.Boolean):
    pass

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'MyBool'


class MyNull(asn1.Null):
    pass

    __typing__ = 'MyNull'


class MyInt(asn1.Integer):
    constraints = 'SIZE(0 .. 100)'

    def init_value(self):
        return 0 if 0 <= 0 <= 100 else 0

    @classmethod
    def check_constraints(cls, value):
        result = 0 <= value <= 100
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 0, 100)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 0, 100)

    __typing__ = 'MyInt'


class MyInt2(asn1.Integer):
    constraints = 'SIZE(3 .. 66)'

    def init_value(self):
        return 0 if 3 <= 0 <= 66 else 3

    @classmethod
    def check_constraints(cls, value):
        result = 3 <= value <= 66
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 3, 66)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 3, 66)

    __typing__ = 'MyInt2'


class MyStr(asn1.IA5String):
    constraints = 'SIZE(1 .. 10)'

    def init_value(self):
        return get_string_init_char(self) * 1

    @classmethod
    def check_constraints(cls, value):
        result = 1 <= len(value) <= 10
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 1, 10)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 1, 10)

    __typing__ = 'MyStr'


class MyNumStr(asn1.NumericString):
    constraints = 'SIZE(3)'

    def init_value(self):
        return get_string_init_char(self) * 3

    @classmethod
    def check_constraints(cls, value):
        result = len(value) == 3
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 3, 3)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 3, 3)

    __typing__ = 'MyNumStr'


class MyBit(asn1.BitString):
    constraints = 'SIZE(16 .. 202)'

    def init_value(self):
        return get_string_init_char(self) * 16

    @classmethod
    def check_constraints(cls, value):
        result = 16 <= len(value) <= 202
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 16, 202)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 16, 202)

    __typing__ = 'MyBit'


class MyOct(asn1.OctetString):
    constraints = 'SIZE(3 .. 8)'

    def init_value(self):
        return get_string_init_char(self) * 3

    @classmethod
    def check_constraints(cls, value):
        result = 3 <= len(value) <= 8
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 3, 8)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 3, 8)

    __typing__ = 'MyOct'


class MyReal(asn1.Real):
    constraints = 'SIZE(1.00000000000000000000E+001 .. 2.60000000000000000000E+001)'

    def init_value(self):
        return 0 if 1.00000000000000000000E+001 <= 0 <= 2.60000000000000000000E+001 else 1.00000000000000000000E+001

    @classmethod
    def check_constraints(cls, value):
        result = 1.00000000000000000000E+001 <= value <= 2.60000000000000000000E+001
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 1.00000000000000000000E+001, 2.60000000000000000000E+001)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 1.00000000000000000000E+001, 2.60000000000000000000E+001)

    __typing__ = 'MyReal'


class MyReal2(MyReal):
    pass

    __typing__ = 'MyReal2'


class MyIntArr(asn1.SequenceOf):
    class _ElementType(asn1.Integer):
        constraints = 'SIZE(0 .. 3)'

        def init_value(self):
            return 0 if 0 <= 0 <= 3 else 0

        @classmethod
        def check_constraints(cls, value):
            result = 0 <= value <= 3
            return result

        @classmethod
        def _uper_encode(cls, bit_stream, value):
            cls._default_uper_encode(bit_stream, value, 0, 3)

        @classmethod
        def _uper_decode(cls, bit_stream):
            return cls._default_uper_decode(bit_stream, 0, 3)

    __element__ = _ElementType

    constraints = 'SIZE(10 .. 10)'

    def init_value(self):
        return 10  # array size

    @classmethod
    def check_constraints(self, value):
        result = 10 <= len(value) <= 10
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 10, 10)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 10, 10)

    __typing__ = 'MyIntArr'


class MyEnum(asn1.Enumerated):
    class Value(asn1.Enumerated.Value):
        NONE = None
        alpha = 0
        beta = 1
        gamma = 2

    __base__ = Value

    # for global access
    add_globals(
        alpha = 0,
        beta = 1,
        gamma = 2
    )

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'MyEnum'


class MyStruct(asn1.Sequence):
    def __init__(self, source=None):
        self.attributes = dict()
        self.optionals = list()

        # a
        class _aType(asn1.Integer):
            constraints = 'SIZE(1 .. 10)'

            def init_value(self):
                return 0 if 1 <= 0 <= 10 else 1

            @classmethod
            def check_constraints(cls, value):
                result = 1 <= value <= 10
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 1, 10)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 1, 10)

            __typing__ = 'a'

        self.aType = _aType
        self.a: self.aType.__typing__ = self.aType()
        self.attributes['a'] = True

        # b
        class _bType(asn1.Real):
            constraints = 'SIZE(MIN .. MAX)'

            def init_value(self):
                return 0 if MIN <= 0 <= MAX else MIN

            @classmethod
            def check_constraints(cls, value):
                result = MIN <= value <= MAX
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, MIN, MAX)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, MIN, MAX)

            __typing__ = 'b'

        self.bType = _bType
        self.b: self.bType.__typing__ = self.bType()
        self.attributes['b'] = True
        self.optionals.append('b')

        # c
        class _cType(MyEnum):
            pass

            __typing__ = 'c'

        self.cType = _cType
        self.c: self.cType.__typing__ = self.cType()
        self.attributes['c'] = True
        self.optionals.append('c')

        self.initialized = True
        self._init_from_source(source)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'MyStruct'


class MyStructArr(asn1.SequenceOf):
    class _ElementType(MyStruct):
        pass

    __element__ = _ElementType

    constraints = 'SIZE(2 .. 4)'

    def init_value(self):
        return 2  # array size

    @classmethod
    def check_constraints(self, value):
        result = 2 <= len(value) <= 4
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 2, 4)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 2, 4)

    __typing__ = 'MyStructArr'


class MyChoice(asn1.Choice):
    def __init__(self, choice=None):
        self.attributes = dict()

        # alpha
        class _alphaType(MyStruct):
            pass

            __typing__ = 'alpha'

        self.alphaType = _alphaType
        self.alpha: self.alphaType.__typing__ = self.alphaType()
        self.attributes['alpha'] = False

        # beta
        class _betaType(asn1.Integer):
            constraints = 'SIZE(MIN .. MAX)'

            def init_value(self):
                return 0 if MIN <= 0 <= MAX else MIN

            @classmethod
            def check_constraints(cls, value):
                result = MIN <= value <= MAX
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, MIN, MAX)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, MIN, MAX)

            __typing__ = 'beta'

        self.betaType = _betaType
        self.beta: self.betaType.__typing__ = self.betaType()
        self.attributes['beta'] = False

        # octStr
        class _octStrType(asn1.OctetString):
            constraints = 'SIZE(4)'

            def init_value(self):
                return get_string_init_char(self) * 4

            @classmethod
            def check_constraints(cls, value):
                result = len(value) == 4
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 4, 4)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 4, 4)

            __typing__ = 'octStr'

        self.octStrType = _octStrType
        self.octStr: self.octStrType.__typing__ = self.octStrType()
        self.attributes['octStr'] = False

        self.initialized = True
        self._init_choice(choice)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'MyChoice'


class MySqOf(asn1.SequenceOf):
    class _ElementType(asn1.Sequence):
        def __init__(self, source=None):
            self.attributes = dict()
            self.optionals = list()

            # a2
            class _a2Type(asn1.Integer):
                constraints = 'SIZE(1 .. 10)'

                def init_value(self):
                    return 0 if 1 <= 0 <= 10 else 1

                @classmethod
                def check_constraints(cls, value):
                    result = 1 <= value <= 10
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, 1, 10)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, 1, 10)

                __typing__ = 'a2'

            self.a2Type = _a2Type
            self.a2: self.a2Type.__typing__ = self.a2Type()
            self.attributes['a2'] = True

            # b2
            class _b2Type(asn1.Real):
                constraints = 'SIZE(MIN .. MAX)'

                def init_value(self):
                    return 0 if MIN <= 0 <= MAX else MIN

                @classmethod
                def check_constraints(cls, value):
                    result = MIN <= value <= MAX
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, MIN, MAX)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, MIN, MAX)

                __typing__ = 'b2'

            self.b2Type = _b2Type
            self.b2: self.b2Type.__typing__ = self.b2Type()
            self.attributes['b2'] = True
            self.optionals.append('b2')

            # c2
            class _c2Type(asn1.Integer):
                constraints = 'SIZE(MIN .. MAX)'

                def init_value(self):
                    return 0 if MIN <= 0 <= MAX else MIN

                @classmethod
                def check_constraints(cls, value):
                    result = MIN <= value <= MAX
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, MIN, MAX)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, MIN, MAX)

                __typing__ = 'c2'

            self.c2Type = _c2Type
            self.c2: self.c2Type.__typing__ = self.c2Type()
            self.attributes['c2'] = True
            self.optionals.append('c2')

            self.initialized = True
            self._init_from_source(source)

        @classmethod
        def _uper_encode(cls, bit_stream, value):
            cls._default_uper_encode(bit_stream, value)

        @classmethod
        def _uper_decode(cls, bit_stream):
            return cls._default_uper_decode(bit_stream)

    __element__ = _ElementType

    constraints = 'SIZE(1 .. 25)'

    def init_value(self):
        return 1  # array size

    @classmethod
    def check_constraints(self, value):
        result = 1 <= len(value) <= 25
        return result

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value, 1, 25)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream, 1, 25)

    __typing__ = 'MySqOf'


class TypeEnumerated(asn1.Enumerated):
    class Value(asn1.Enumerated.Value):
        NONE = None
        red = 0
        green = 1
        blue = 2

    __base__ = Value

    # for global access
    add_globals(
        red = 0,
        green = 1,
        blue = 2
    )

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'TypeEnumerated'


class My2ndEnumerated(TypeEnumerated):
    pass

    __typing__ = 'My2ndEnumerated'


class AComplexMessage(asn1.Sequence):
    def __init__(self, source=None):
        self.attributes = dict()
        self.optionals = list()

        # intVal
        class _intValType(asn1.Integer):
            constraints = 'SIZE(0 .. 10)'

            def init_value(self):
                return 0 if 0 <= 0 <= 10 else 0

            @classmethod
            def check_constraints(cls, value):
                result = 0 <= value <= 10
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 0, 10)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 0, 10)

            __typing__ = 'intVal'

        self.intValType = _intValType
        self.intVal: self.intValType.__typing__ = self.intValType()
        self.attributes['intVal'] = True

        # int2Val
        class _int2ValType(asn1.Integer):
            constraints = 'SIZE(-10 .. 10)'

            def init_value(self):
                return 0 if -10 <= 0 <= 10 else -10

            @classmethod
            def check_constraints(cls, value):
                result = -10 <= value <= 10
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, -10, 10)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, -10, 10)

            __typing__ = 'int2Val'

        self.int2ValType = _int2ValType
        self.int2Val: self.int2ValType.__typing__ = self.int2ValType()
        self.attributes['int2Val'] = True

        # int3Val
        class _int3ValType(MyInt):
            pass

            __typing__ = 'int3Val'

        self.int3ValType = _int3ValType
        self.int3Val: self.int3ValType.__typing__ = self.int3ValType()
        self.attributes['int3Val'] = True

        # strVal
        class _strValType(MyStr):
            pass

            __typing__ = 'strVal'

        self.strValType = _strValType
        self.strVal: self.strValType.__typing__ = self.strValType()
        self.attributes['strVal'] = True

        # intArray
        class _intArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Integer):
                constraints = 'SIZE(0 .. 3)'

                def init_value(self):
                    return 0 if 0 <= 0 <= 3 else 0

                @classmethod
                def check_constraints(cls, value):
                    result = 0 <= value <= 3
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, 0, 3)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, 0, 3)

            __element__ = _ElementType

            constraints = 'SIZE(10 .. 10)'

            def init_value(self):
                return 10  # array size

            @classmethod
            def check_constraints(self, value):
                result = 10 <= len(value) <= 10
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 10, 10)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 10, 10)

            __typing__ = 'intArray'

        self.intArrayType = _intArrayType
        self.intArray: self.intArrayType.__typing__ = self.intArrayType()
        self.attributes['intArray'] = True

        # realArray
        class _realArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Real):
                constraints = 'SIZE(1.00000000000000010000E-001 .. 3.14000000000000010000E+000)'

                def init_value(self):
                    return 0 if 1.00000000000000010000E-001 <= 0 <= 3.14000000000000010000E+000 else 1.00000000000000010000E-001

                @classmethod
                def check_constraints(cls, value):
                    result = 1.00000000000000010000E-001 <= value <= 3.14000000000000010000E+000
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, 1.00000000000000010000E-001, 3.14000000000000010000E+000)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, 1.00000000000000010000E-001, 3.14000000000000010000E+000)

            __element__ = _ElementType

            constraints = 'SIZE(15 .. 15)'

            def init_value(self):
                return 15  # array size

            @classmethod
            def check_constraints(self, value):
                result = 15 <= len(value) <= 15
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 15, 15)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 15, 15)

            __typing__ = 'realArray'

        self.realArrayType = _realArrayType
        self.realArray: self.realArrayType.__typing__ = self.realArrayType()
        self.attributes['realArray'] = True

        # octStrArray
        class _octStrArrayType(asn1.SequenceOf):
            class _ElementType(asn1.OctetString):
                constraints = 'SIZE(1 .. 10)'

                def init_value(self):
                    return get_string_init_char(self) * 1

                @classmethod
                def check_constraints(cls, value):
                    result = 1 <= len(value) <= 10
                    return result

                @classmethod
                def _uper_encode(cls, bit_stream, value):
                    cls._default_uper_encode(bit_stream, value, 1, 10)

                @classmethod
                def _uper_decode(cls, bit_stream):
                    return cls._default_uper_decode(bit_stream, 1, 10)

            __element__ = _ElementType

            constraints = 'SIZE(20 .. 20)'

            def init_value(self):
                return 20  # array size

            @classmethod
            def check_constraints(self, value):
                result = 20 <= len(value) <= 20
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 20, 20)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 20, 20)

            __typing__ = 'octStrArray'

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

            @classmethod
            def check_constraints(self, value):
                result = 12 <= len(value) <= 12
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 12, 12)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 12, 12)

            __typing__ = 'enumArray'

        self.enumArrayType = _enumArrayType
        self.enumArray: self.enumArrayType.__typing__ = self.enumArrayType()
        self.attributes['enumArray'] = True

        # enumValue
        class _enumValueType(TypeEnumerated):
            pass

            __typing__ = 'enumValue'

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
            add_globals(
                truism = 0,
                falsism = 1
            )

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream)

            __typing__ = 'enumValue2'

        self.enumValue2Type = _enumValue2Type
        self.enumValue2: self.enumValue2Type.__typing__ = self.enumValue2Type()
        self.attributes['enumValue2'] = True

        # label
        class _labelType(asn1.OctetString):
            constraints = 'SIZE(10 .. 40)'

            def init_value(self):
                return get_string_init_char(self) * 10

            @classmethod
            def check_constraints(cls, value):
                result = 10 <= len(value) <= 40
                return result

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value, 10, 40)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream, 10, 40)

            __typing__ = 'label'

        self.labelType = _labelType
        self.label: self.labelType.__typing__ = self.labelType()
        self.attributes['label'] = True

        # bAlpha
        class _bAlphaType(asn1.Boolean):
            pass

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream)

            __typing__ = 'bAlpha'

        self.bAlphaType = _bAlphaType
        self.bAlpha: self.bAlphaType.__typing__ = self.bAlphaType()
        self.attributes['bAlpha'] = True

        # bBeta
        class _bBetaType(asn1.Boolean):
            pass

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream)

            __typing__ = 'bBeta'

        self.bBetaType = _bBetaType
        self.bBeta: self.bBetaType.__typing__ = self.bBetaType()
        self.attributes['bBeta'] = True

        self.initialized = True
        self._init_from_source(source)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)

    __typing__ = 'AComplexMessage'


# vMyBool
class _vMyBoolType(MyBool):
    pass

    __typing__ = 'vMyBool'


vMyBool: _vMyBoolType.__typing__ = _vMyBoolType(True)


# vMyInt
class _vMyIntType(MyInt):
    pass

    __typing__ = 'vMyInt'


vMyInt: _vMyIntType.__typing__ = _vMyIntType(88)


# v2MyInt
class _v2MyIntType(MyInt):
    pass

    __typing__ = 'v2MyInt'


v2MyInt: _v2MyIntType.__typing__ = _v2MyIntType(eval('vMyInt'))


# vMyStr
class _vMyStrType(MyStr):
    pass

    __typing__ = 'vMyStr'


vMyStr: _vMyStrType.__typing__ = _vMyStrType("AAABBC")


# vMyNumStr
class _vMyNumStrType(MyNumStr):
    pass

    __typing__ = 'vMyNumStr'


vMyNumStr: _vMyNumStrType.__typing__ = _vMyNumStrType("123")


# vMyBit
class _vMyBitType(MyBit):
    pass

    __typing__ = 'vMyBit'


vMyBit: _vMyBitType.__typing__ = _vMyBitType(bytes.fromhex('FFAC'))


# vMyOct
class _vMyOctType(MyOct):
    pass

    __typing__ = 'vMyOct'


vMyOct: _vMyOctType.__typing__ = _vMyOctType(bytes.fromhex('12345678'))


# vMyReal
class _vMyRealType(MyReal):
    pass

    __typing__ = 'vMyReal'


vMyReal: _vMyRealType.__typing__ = _vMyRealType(1.71230000000000010000E+001)


# vMyIntArr
class _vMyIntArrType(MyIntArr):
    pass

    __typing__ = 'vMyIntArr'


vMyIntArr: _vMyIntArrType.__typing__ = _vMyIntArrType([1, 2, 3, 1, 2, 3, 0, 1, 0, 2])


# vMyEnum
class _vMyEnumType(MyEnum):
    pass

    __typing__ = 'vMyEnum'


vMyEnum: _vMyEnumType.__typing__ = _vMyEnumType(eval('alpha'))


# vMyStruct
class _vMyStructType(MyStruct):
    pass

    __typing__ = 'vMyStruct'


vMyStruct: _vMyStructType.__typing__ = _vMyStructType(dict(a=2, c=eval('alpha')))


# vMyMyStruct
class _vMyMyStructType(MyStructArr):
    pass

    __typing__ = 'vMyMyStruct'


vMyMyStruct: _vMyMyStructType.__typing__ = _vMyMyStructType([dict(a=4, c=eval('beta')), dict(a=10, c=eval('gamma'), b=7.88999999999999970000E+000)])


# vMyChoice
class _vMyChoiceType(MyChoice):
    pass

    __typing__ = 'vMyChoice'


vMyChoice: _vMyChoiceType.__typing__ = _vMyChoiceType(choice=dict(name='alpha', value=dict(a=2, b=1.23234000000000000000E+002, c=eval('alpha'))))


# End
x = MyStr('asd')
y=MyStr('asd')
print(x,'asdasd'+y.get(), x==y)