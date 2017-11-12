# ASN.1 Data model

import asn1
import typing

MAX = asn1.INT_MAX
MIN = asn1.INT_MIN
INF = asn1.INFINITY
NAN = asn1.NAN


def get_string_init_char(obj):
    if issubclass(obj, asn1.NumericString) or issubclass(obj, asn1.BitString):
        return '0'
    elif issubclass(obj, asn1.OctetString):
        return b'0'
    else:
        return ' '


def add_globals(**kwargs):
    for name, value in kwargs.items():
        globals()[name] = value


class MyBool(asn1.Boolean):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Boolean.__typing__, asn1.Boolean]:
        return object.__new__(cls)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)


class MyNull(asn1.Null):
    pass


class MyInt(asn1.Integer):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
        return object.__new__(cls)

    constraints = 'SIZE(0 .. 100)'

    @classmethod
    def init_value(cls):
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


class MyInt2(asn1.Integer):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
        return object.__new__(cls)

    constraints = 'SIZE(3 .. 66)'

    @classmethod
    def init_value(cls):
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


class MyStr(asn1.IA5String):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.IA5String.__typing__, asn1.IA5String]:
        return object.__new__(cls)

    constraints = 'SIZE(1 .. 10)'

    @classmethod
    def init_value(cls):
        return get_string_init_char(cls) * 1

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


class MyNumStr(asn1.NumericString):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.NumericString.__typing__, asn1.NumericString]:
        return object.__new__(cls)

    constraints = 'SIZE(3)'

    @classmethod
    def init_value(cls):
        return get_string_init_char(cls) * 3

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


class MyBit(asn1.BitString):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.BitString.__typing__, asn1.BitString]:
        return object.__new__(cls)

    constraints = 'SIZE(16 .. 202)'

    @classmethod
    def init_value(cls):
        return get_string_init_char(cls) * 16

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


class MyOct(asn1.OctetString):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.OctetString.__typing__, asn1.OctetString]:
        return object.__new__(cls)

    constraints = 'SIZE(3 .. 8)'

    @classmethod
    def init_value(cls):
        return get_string_init_char(cls) * 3

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


class MyReal(asn1.Real):
    def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Real.__typing__, asn1.Real]:
        return object.__new__(cls)

    constraints = 'SIZE(1.00000000000000000000E+001 .. 2.60000000000000000000E+001)'

    @classmethod
    def init_value(cls):
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


class MyReal2(MyReal):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyReal.__typing__, MyReal]:
        return object.__new__(cls)


class MyIntArr(asn1.SequenceOf):
    class _ElementType(asn1.Integer):
        def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
            return object.__new__(cls)

        constraints = 'SIZE(0 .. 3)'

        @classmethod
        def init_value(cls):
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

    @classmethod
    def init_value(cls):
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


class MyStruct(asn1.Sequence):
    def __init__(self, source=None):
        self.attributes = dict()
        self.optionals = list()

        # a
        class _aType(asn1.Integer):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                return object.__new__(cls)

            constraints = 'SIZE(1 .. 10)'

            @classmethod
            def init_value(cls):
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

        self.aType = _aType
        self.a = self.aType()
        self.attributes['a'] = True

        # b
        class _bType(asn1.Real):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Real.__typing__, asn1.Real]:
                return object.__new__(cls)

            constraints = 'SIZE(MIN .. MAX)'

            @classmethod
            def init_value(cls):
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

        self.bType = _bType
        self.b = self.bType()
        self.attributes['b'] = True
        self.optionals.append('b')

        # c
        class _cType(MyEnum):
            def __new__(cls, *args, **kwargs) -> typing.Union[MyEnum.__typing__, MyEnum]:
                return object.__new__(cls)

        self.cType = _cType
        self.c = self.cType()
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


class MyStructArr(asn1.SequenceOf):
    class _ElementType(MyStruct):
        def __new__(cls, *args, **kwargs) -> typing.Union[MyStruct.__typing__, MyStruct]:
            return object.__new__(cls)

    __element__ = _ElementType

    constraints = 'SIZE(2 .. 4)'

    @classmethod
    def init_value(cls):
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


class MyChoice(asn1.Choice):
    def __init__(self, choice=None):
        self.attributes = dict()

        # alpha
        class _alphaType(MyStruct):
            def __new__(cls, *args, **kwargs) -> typing.Union[MyStruct.__typing__, MyStruct]:
                return object.__new__(cls)

        self.alphaType = _alphaType
        self.alpha = self.alphaType()
        self.attributes['alpha'] = False

        # beta
        class _betaType(asn1.Integer):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                return object.__new__(cls)

            constraints = 'SIZE(MIN .. MAX)'

            @classmethod
            def init_value(cls):
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

        self.betaType = _betaType
        self.beta = self.betaType()
        self.attributes['beta'] = False

        # octStr
        class _octStrType(asn1.OctetString):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.OctetString.__typing__, asn1.OctetString]:
                return object.__new__(cls)

            constraints = 'SIZE(4)'

            @classmethod
            def init_value(cls):
                return get_string_init_char(cls) * 4

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

        self.octStrType = _octStrType
        self.octStr = self.octStrType()
        self.attributes['octStr'] = False

        self.initialized = True
        self._init_choice(choice)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)


class MySqOf(asn1.SequenceOf):
    class _ElementType(asn1.Sequence):
        def __init__(self, source=None):
            self.attributes = dict()
            self.optionals = list()

            # a2
            class _a2Type(asn1.Integer):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                    return object.__new__(cls)

                constraints = 'SIZE(1 .. 10)'

                @classmethod
                def init_value(cls):
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

            self.a2Type = _a2Type
            self.a2 = self.a2Type()
            self.attributes['a2'] = True

            # b2
            class _b2Type(asn1.Real):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Real.__typing__, asn1.Real]:
                    return object.__new__(cls)

                constraints = 'SIZE(MIN .. MAX)'

                @classmethod
                def init_value(cls):
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

            self.b2Type = _b2Type
            self.b2 = self.b2Type()
            self.attributes['b2'] = True
            self.optionals.append('b2')

            # c2
            class _c2Type(asn1.Integer):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                    return object.__new__(cls)

                constraints = 'SIZE(MIN .. MAX)'

                @classmethod
                def init_value(cls):
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

            self.c2Type = _c2Type
            self.c2 = self.c2Type()
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

    @classmethod
    def init_value(cls):
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


class My2ndEnumerated(TypeEnumerated):
    def __new__(cls, *args, **kwargs) -> typing.Union[TypeEnumerated.__typing__, TypeEnumerated]:
        return object.__new__(cls)


class AComplexMessage(asn1.Sequence):
    def __init__(self, source=None):
        self.attributes = dict()
        self.optionals = list()

        # intVal
        class _intValType(asn1.Integer):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                return object.__new__(cls)

            constraints = 'SIZE(0 .. 10)'

            @classmethod
            def init_value(cls):
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

        self.intValType = _intValType
        self.intVal = self.intValType()
        self.attributes['intVal'] = True

        # int2Val
        class _int2ValType(asn1.Integer):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                return object.__new__(cls)

            constraints = 'SIZE(-10 .. 10)'

            @classmethod
            def init_value(cls):
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

        self.int2ValType = _int2ValType
        self.int2Val = self.int2ValType()
        self.attributes['int2Val'] = True

        # int3Val
        class _int3ValType(MyInt):
            def __new__(cls, *args, **kwargs) -> typing.Union[MyInt.__typing__, MyInt]:
                return object.__new__(cls)

        self.int3ValType = _int3ValType
        self.int3Val = self.int3ValType()
        self.attributes['int3Val'] = True

        # strVal
        class _strValType(MyStr):
            def __new__(cls, *args, **kwargs) -> typing.Union[MyStr.__typing__, MyStr]:
                return object.__new__(cls)

        self.strValType = _strValType
        self.strVal = self.strValType()
        self.attributes['strVal'] = True

        # intArray
        class _intArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Integer):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Integer.__typing__, asn1.Integer]:
                    return object.__new__(cls)

                constraints = 'SIZE(0 .. 3)'

                @classmethod
                def init_value(cls):
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

            @classmethod
            def init_value(cls):
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

        self.intArrayType = _intArrayType
        self.intArray = self.intArrayType()
        self.attributes['intArray'] = True

        # realArray
        class _realArrayType(asn1.SequenceOf):
            class _ElementType(asn1.Real):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Real.__typing__, asn1.Real]:
                    return object.__new__(cls)

                constraints = 'SIZE(1.00000000000000010000E-001 .. 3.14000000000000010000E+000)'

                @classmethod
                def init_value(cls):
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

            @classmethod
            def init_value(cls):
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

        self.realArrayType = _realArrayType
        self.realArray = self.realArrayType()
        self.attributes['realArray'] = True

        # octStrArray
        class _octStrArrayType(asn1.SequenceOf):
            class _ElementType(asn1.OctetString):
                def __new__(cls, *args, **kwargs) -> typing.Union[asn1.OctetString.__typing__, asn1.OctetString]:
                    return object.__new__(cls)

                constraints = 'SIZE(1 .. 10)'

                @classmethod
                def init_value(cls):
                    return get_string_init_char(cls) * 1

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

            @classmethod
            def init_value(cls):
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

        self.octStrArrayType = _octStrArrayType
        self.octStrArray = self.octStrArrayType()
        self.attributes['octStrArray'] = True

        # enumArray
        class _enumArrayType(asn1.SequenceOf):
            class _ElementType(TypeEnumerated):
                def __new__(cls, *args, **kwargs) -> typing.Union[TypeEnumerated.__typing__, TypeEnumerated]:
                    return object.__new__(cls)

            __element__ = _ElementType

            constraints = 'SIZE(12 .. 12)'

            @classmethod
            def init_value(cls):
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

        self.enumArrayType = _enumArrayType
        self.enumArray = self.enumArrayType()
        self.attributes['enumArray'] = True

        # enumValue
        class _enumValueType(TypeEnumerated):
            def __new__(cls, *args, **kwargs) -> typing.Union[TypeEnumerated.__typing__, TypeEnumerated]:
                return object.__new__(cls)

        self.enumValueType = _enumValueType
        self.enumValue = self.enumValueType()
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

        self.enumValue2Type = _enumValue2Type
        self.enumValue2 = self.enumValue2Type()
        self.attributes['enumValue2'] = True

        # label
        class _labelType(asn1.OctetString):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.OctetString.__typing__, asn1.OctetString]:
                return object.__new__(cls)

            constraints = 'SIZE(10 .. 40)'

            @classmethod
            def init_value(cls):
                return get_string_init_char(cls) * 10

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

        self.labelType = _labelType
        self.label = self.labelType()
        self.attributes['label'] = True

        # bAlpha
        class _bAlphaType(asn1.Boolean):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Boolean.__typing__, asn1.Boolean]:
                return object.__new__(cls)

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream)

        self.bAlphaType = _bAlphaType
        self.bAlpha = self.bAlphaType()
        self.attributes['bAlpha'] = True

        # bBeta
        class _bBetaType(asn1.Boolean):
            def __new__(cls, *args, **kwargs) -> typing.Union[asn1.Boolean.__typing__, asn1.Boolean]:
                return object.__new__(cls)

            @classmethod
            def _uper_encode(cls, bit_stream, value):
                cls._default_uper_encode(bit_stream, value)

            @classmethod
            def _uper_decode(cls, bit_stream):
                return cls._default_uper_decode(bit_stream)

        self.bBetaType = _bBetaType
        self.bBeta = self.bBetaType()
        self.attributes['bBeta'] = True

        self.initialized = True
        self._init_from_source(source)

    @classmethod
    def _uper_encode(cls, bit_stream, value):
        cls._default_uper_encode(bit_stream, value)

    @classmethod
    def _uper_decode(cls, bit_stream):
        return cls._default_uper_decode(bit_stream)


# vMyBool
class _vMyBoolType(MyBool):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyBool.__typing__, MyBool]:
        return object.__new__(cls)


vMyBool = _vMyBoolType(True)


# vMyInt
class _vMyIntType(MyInt):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyInt.__typing__, MyInt]:
        return object.__new__(cls)


vMyInt = _vMyIntType(88)


# v2MyInt
class _v2MyIntType(MyInt):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyInt.__typing__, MyInt]:
        return object.__new__(cls)


v2MyInt = _v2MyIntType(eval('vMyInt'))


# vMyStr
class _vMyStrType(MyStr):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyStr.__typing__, MyStr]:
        return object.__new__(cls)


vMyStr = _vMyStrType("AAABBC")


# vMyNumStr
class _vMyNumStrType(MyNumStr):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyNumStr.__typing__, MyNumStr]:
        return object.__new__(cls)


vMyNumStr = _vMyNumStrType("123")


# vMyBit
class _vMyBitType(MyBit):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyBit.__typing__, MyBit]:
        return object.__new__(cls)


vMyBit = _vMyBitType(bytes.fromhex('FFAC'))


# vMyOct
class _vMyOctType(MyOct):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyOct.__typing__, MyOct]:
        return object.__new__(cls)


vMyOct = _vMyOctType(bytes.fromhex('12345678'))


# vMyReal
class _vMyRealType(MyReal):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyReal.__typing__, MyReal]:
        return object.__new__(cls)


vMyReal = _vMyRealType(1.71230000000000010000E+001)


# vMyIntArr
class _vMyIntArrType(MyIntArr):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyIntArr.__typing__, MyIntArr]:
        return object.__new__(cls)


vMyIntArr = _vMyIntArrType([1, 2, 3, 1, 2, 3, 0, 1, 0, 2])


# vMyEnum
class _vMyEnumType(MyEnum):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyEnum.__typing__, MyEnum]:
        return object.__new__(cls)


vMyEnum = _vMyEnumType(eval('alpha'))


# vMyStruct
class _vMyStructType(MyStruct):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyStruct.__typing__, MyStruct]:
        return object.__new__(cls)


vMyStruct = _vMyStructType(dict(a=2, c=eval('alpha')))


# vMyMyStruct
class _vMyMyStructType(MyStructArr):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyStructArr.__typing__, MyStructArr]:
        return object.__new__(cls)


vMyMyStruct = _vMyMyStructType([dict(a=4, c=eval('beta')), dict(a=10, c=eval('gamma'), b=7.88999999999999970000E+000)])


# vMyChoice
class _vMyChoiceType(MyChoice):
    def __new__(cls, *args, **kwargs) -> typing.Union[MyChoice.__typing__, MyChoice]:
        return object.__new__(cls)


vMyChoice = _vMyChoiceType(choice=dict(name='alpha', value=dict(a=2, b=1.23234000000000000000E+002, c=eval('alpha'))))


# End
