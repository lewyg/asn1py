import sys
import typing
from enum import Enum

WORD_SIZE = 8
INT_MAX = sys.maxsize
INT_MIN = -sys.maxsize
DBL_MAX = sys.float_info.max
DBL_MIN = sys.float_info.min
INFINITY = float('inf')
NAN = float('nan')


#############################
#        Exceptions         #
#############################

class ASN1Erorr(Exception):
    pass


class ConstraintException(ASN1Erorr):
    def __init__(self, class_name, value, constraints, expected_type):
        message = "Constraint failed! {} object can't be {} ( {} - {} )".format(
            class_name, value, constraints, expected_type
        )
        super().__init__(message)


#############################
#         bitarray          #
#############################


class bitarray:
    def __init__(self, source=None):
        self._data = bytearray()
        self._bitsize = 0

        if isinstance(source, int) and source > 0:
            self._init_from_size(source)

        elif self.__iterable_bits(source):
            self._init_from_iterable(source)

        elif isinstance(source, bytearray) or isinstance(source, bytes):
            self._init_from_bytes(source)

    def _init_from_size(self, size):
        self._data = bytearray(get_byte_length_from_bit_length(size))
        self._bitsize = size

    def _init_from_iterable(self, source):
        self.__append_bits(source)

    def _init_from_bytes(self, source):
        self._data = bytearray(source)
        self._bitsize = len(self._data) * WORD_SIZE

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__get_slice(item)

        self.__assert_correct_index(item)

        bit_position = self.__get_bit_position(item)
        byte_position = self.__get_byte_position(item)

        byte = self._data[byte_position]
        byte >>= bit_position
        bit = byte & 0b00000001

        return bit

    def __get_slice(self, item):
        start = item.start or 0
        if start < 0:
            start = self._bitsize + start

        elif start >= self._bitsize:
            start = self._bitsize - 1

        stop = item.stop or self._bitsize
        if stop < 0:
            stop = self._bitsize + stop

        elif stop >= self._bitsize:
            stop = self._bitsize

        return bitarray([self[i] for i in range(start, stop, item.step or 1)])

    def __setitem__(self, item, value):
        self.__assert_correct_index(item)
        self.__assert_bit(value)

        bit_position = self.__get_bit_position(item)
        byte_position = self.__get_byte_position(item)

        byte = self._data[byte_position]
        byte = self.__set_bit(byte, bit_position) if value else self.__clear_bit(byte, bit_position)
        self._data[byte_position] = byte

    def __delitem__(self, item):
        self.__assert_correct_index(item)

        for i in range(item, self._bitsize - 1):
            self[i] = self[i + 1]

        self[self._bitsize - 1] = 0
        self._bitsize -= 1

    def __add__(self, other):
        if self.__iterable_bits(other):
            self.__append_bits(other)

        elif is_bit(other):
            self.append(int(other))

        else:
            raise TypeError("Can't add '{}' to bitarray implicitly".format(other))

        return self

    def __eq__(self, other):
        for i, b in enumerate(self):
            if str(b) != str(other[i]):
                return False

        return True

    def __iter__(self):
        self._n = 0
        return self

    def __next__(self):
        if self._n < self._bitsize:
            element = self[self._n]
            self._n += 1
            return element

        else:
            raise StopIteration

    def __len__(self):
        return self._bitsize

    def __repr__(self):
        return str([bit for bit in self])

    def __str__(self):
        return ''.join([str(bit) for bit in self])

    def __getattr__(self, item):
        raise AttributeError("'bitarray' object has no attribute '{}'".format(item))

    def append(self, bit):
        self.__assert_bit(bit)

        if self._bitsize % WORD_SIZE:
            byte = self._data.pop()
        else:
            byte = 0b00000000

        bit_position = self.__get_bit_position(self._bitsize)
        byte = self.__set_bit(byte, bit_position) if bit else self.__clear_bit(byte, bit_position)

        self._bitsize += 1
        self._data.append(byte)

    def append_byte(self, byte):
        if self._bitsize % WORD_SIZE:
            old_byte = self._data.pop()
            bit_position = self.__get_bit_position(self._bitsize)
            old_byte |= byte >> (WORD_SIZE - bit_position - 1)
            self._data.append(old_byte)
            self._data.append((byte << (bit_position + 1)) & 0b11111111)

        else:
            self._data.append(byte)

        self._bitsize += WORD_SIZE

    def insert(self, index, value):
        self.__assert_correct_index(index)
        self.__assert_bit(value)

        self.append(0)

        for i in range(self._bitsize - 1, index, -1):
            self[i] = self[i - 1]

        self[index] = int(value)

    def pop(self, index=None):
        index = index or self._bitsize - 1
        self.__assert_correct_index(index)

        bit = self[index]
        del self[index]

        return bit

    def remove(self, index=None):
        index = index or self._bitsize - 1
        self.__assert_correct_index(index)

        del self[index]

        return self

    def reverse(self):
        new = self.copy()

        for i, b in enumerate(self):
            new[self._bitsize - i - 1] = b

        return new

    def clear(self):
        self._data = bytearray()
        self._bitsize = 0

    def bytes(self):
        return self._data

    def copy(self):
        return bitarray(self)

    def extend(self, other):
        if self.__iterable_bits(other):
            self.__append_bits(other)

    @classmethod
    def fromhex(cls, s):
        return bitarray(bytearray.fromhex(s))

    def hex(self):
        return self._data.hex()

    def __append_bits(self, bit_iterable):
        for c in bit_iterable:
            self.append(int(c))

    @staticmethod
    def __iterable_bits(source):
        return hasattr(source, '__iter__') and all([is_bit(c) for c in source])

    def __assert_correct_index(self, item):
        if 0 <= item >= self._bitsize:
            raise AttributeError("Item {} doesn't exist!".format(item))

    @staticmethod
    def __assert_bit(value):
        if not is_bit(value):
            raise AttributeError("bitarray can't contain {} value".format(value))

    @staticmethod
    def __get_byte_position(position):
        return position // WORD_SIZE

    @staticmethod
    def __get_bit_position(position):
        return WORD_SIZE - position % WORD_SIZE - 1

    @staticmethod
    def __set_bit(byte, bit):
        return byte | (1 << bit)

    @staticmethod
    def __clear_bit(byte, bit):
        return byte & ~(1 << bit)


def is_bit(c):
    return str(c) in ['0', '1']


def get_byte_length_from_bit_length(bit_length):
    return (bit_length + WORD_SIZE - 1) // WORD_SIZE


def negate_byte(value):
    return (1 << WORD_SIZE) - 1 - value


def get_signed_int_byte_length(value: int):
    if value >= 0:
        bit_length = value.bit_length()
    else:
        bit_length = int(-value - 1).bit_length()

    return get_byte_length_from_bit_length(bit_length)


#############################
#    Encoding / Decoding    #
#############################


class BitStream:
    def __init__(self, buffer=0):
        if isinstance(buffer, BitStream):
            buffer = buffer._buffer

        self._buffer = bitarray(buffer)
        self._current_byte = 0
        self._current_bit = 0

    def __len__(self):
        return len(self._buffer)

    def __str__(self):
        return str(self._buffer)

    def __get_current_position(self):
        return self._current_byte * WORD_SIZE + self._current_bit

    def _increment_bit_counter(self):
        self._current_bit += 1
        if self._current_bit == WORD_SIZE:
            self._current_bit = 0

    # append functions

    def append_bit(self, bit):
        self._buffer.append(bit)
        self._increment_bit_counter()

    def append_bit_one(self):
        self.append_bit(1)

    def append_bit_zero(self):
        self.append_bit(0)

    def append_bits_one(self, n_bits):
        for i in range(n_bits):
            self.append_bit_one()

    def append_bits_zero(self, n_bits):
        for i in range(n_bits):
            self.append_bit_zero()

    def append_bits(self, source, n_bits):
        for byte in source:
            if n_bits >= WORD_SIZE:
                self.append_byte(byte)
                n_bits -= WORD_SIZE

            else:
                self.append_partial_byte(byte, n_bits)
                break

    def append_byte(self, byte, negate=False):
        if negate:
            byte = negate_byte(byte)

        self._buffer.append_byte(byte)
        self._current_byte += 1

    def append_byte_one(self):
        self._buffer.append_byte(0b11111111)

    def append_byte_zero(self):
        self._buffer.append_byte(0b00000000)

    def append_partial_byte(self, byte, n_bits, negate=False):
        if negate:
            byte = negate_byte(byte)

        for i in range(n_bits):
            bit = (byte & 0b10000000) >> (WORD_SIZE - 1)
            self.append_bit(bit)
            self._increment_bit_counter()
            byte <<= 1

    # read functions

    def read_bit(self):
        bit = self._buffer[self.__get_current_position()]
        self._increment_bit_counter()

        return bit

    def read_byte(self):
        position = self.__get_current_position()
        byte = int(str(self._buffer[position:position + WORD_SIZE]), 2)
        self._current_byte += 1

        return byte

    def read_bits(self, n_bits):
        result = bytearray()

        for i in range(n_bits // WORD_SIZE):
            result.append(self.read_byte())

        result.append(self.read_partial_byte(n_bits % WORD_SIZE))

        return result

    def read_partial_byte(self, n_bits):
        byte = 0
        for i in range(n_bits):
            bit = self.read_bit()
            byte |= bit << i
            self._increment_bit_counter()

        return byte

    # encoding

    def encode_non_negative_integer32(self, value: int, negate=False):
        bit_length = value.bit_length()

        while bit_length >= WORD_SIZE:
            byte = (value >> (bit_length - WORD_SIZE)) & 0b11111111
            self.append_byte(byte, negate)
            bit_length -= WORD_SIZE

        if bit_length > 0:
            byte = (value & 0b11111111) << WORD_SIZE - bit_length
            self.append_partial_byte(byte, bit_length, negate)

    def encode_non_negative_integer(self, value: int, negate=False):
        if value < 0x100000000:
            self.encode_non_negative_integer32(value, negate)
        else:
            hi = value >> 32
            lo = value & 0xffffffff

            self.encode_non_negative_integer32(hi, negate)
            lo_bits = lo.bit_length()
            self.append_bits_zero(32 - lo_bits)
            self.encode_non_negative_integer32(lo, negate)

    def encode_constraint_number(self, value: int, min_value, max_value):
        range_bit_length = int(max_value - min_value).bit_length()
        value_bit_length = value.bit_length()
        self.append_bits_zero(range_bit_length - value_bit_length)
        self.encode_non_negative_integer(value - min_value)

    def encode_semi_constraint_number(self, value: int, min_value):
        bit_length = (value - min_value).bit_length()
        value_byte_length = get_byte_length_from_bit_length(bit_length)
        self.encode_constraint_number(value_byte_length, 0, 255)
        self.append_bits_zero(value_byte_length * WORD_SIZE - bit_length)
        self.encode_non_negative_integer(value - min_value)

    def encode_number(self, value: int):
        value_byte_length = get_signed_int_byte_length(value)
        self.encode_constraint_number(value_byte_length, 0, 255)

        if value >= 0:
            self.append_bits_zero(value_byte_length * WORD_SIZE - value.bit_length())
            self.encode_non_negative_integer(value)
        else:
            self.append_bits_one(value_byte_length * WORD_SIZE - (-value - 1).bit_length())
            self.encode_non_negative_integer((-value - 1), True)

    def encode_real(self, value: float):
        """
            Bynary encoding will be used
            REAL = M*B^E
            where
            M = S*N*2^F

            ENCODING is done within three parts
            part 1 is 1 byte header
            part 2 is 1 or more byte for exponent
            part 3 is 3 or more byte for mantissa (N)

            First byte
            S :0-->+, S:1-->-1
            Base will be always be 2 (implied by 6th and 5th bit which are zero)
            ab: F  (0..3)
            cd:00 --> 1 byte for exponent as 2's complement
            cd:01 --> 2 byte for exponent as 2's complement
            cd:10 --> 3 byte for exponent as 2's complement
            cd:11 --> 1 byte for encoding the length of the exponent, then the expoent

             8 7 6 5 4 3 2 1
            +-+-+-+-+-+-+-+-+
            |1|S|0|0|a|b|c|d|
            +-+-+-+-+-+-+-+-+
        """

        header = 0x80

        if value == 0:
            self.encode_constraint_number(0, 0, 255)
            return
        elif value == INFINITY:
            self.encode_constraint_number(1, 0, 255)
            self.encode_constraint_number(0x40, 0, 255)
            return
        elif value == -INFINITY:
            self.encode_constraint_number(1, 0, 255)
            self.encode_constraint_number(0x41, 0, 255)
            return
        if value < 0:
            header |= 0x40
            value = -value

        from math import floor, log2
        exponent = int(floor(log2(abs(value))))
        mantissa = value / 2 ** exponent

        while mantissa != int(mantissa) and mantissa < 4503599627370496:
            mantissa *= 2
            exponent -= 1

        mantissa = int(mantissa)

        exp_len = get_signed_int_byte_length(exponent)
        man_len = get_byte_length_from_bit_length(mantissa.bit_length())

        self.encode_constraint_number(1 + exp_len + man_len, 0, 255)
        self.encode_constraint_number(header, 0, 255)

        if exponent > 0:
            self.append_bits_zero(exp_len * WORD_SIZE - exponent.bit_length())
            self.encode_non_negative_integer(exponent)
        else:
            self.append_bits_one(exp_len * WORD_SIZE - (-exponent - 1).bit_length())
            self.encode_non_negative_integer((-exponent - 1), True)

        self.append_bits_zero(man_len * WORD_SIZE - mantissa.bit_length())
        self.encode_non_negative_integer(mantissa)

    # decoding

    def decode_non_negative_integer32(self, n_bits):
        value = 0

        while n_bits >= WORD_SIZE:
            value <<= WORD_SIZE
            value |= self.read_byte()
            n_bits -= WORD_SIZE

        if n_bits:
            value <<= n_bits
            value |= self.read_partial_byte(n_bits)

        return value

    def decode_non_negative_integer(self, n_bits):
        if n_bits <= 32:
            value = self.decode_non_negative_integer32(n_bits)
        else:
            hi = self.decode_non_negative_integer32(32)
            lo = self.decode_non_negative_integer32(n_bits - 32)

            value = hi
            value <<= n_bits - 32
            value |= lo

        return value

    def decode_constraint_number(self, min_value, max_value):
        constraint_range = max_value - min_value
        value = min_value

        if constraint_range != 0:
            value = self.decode_non_negative_integer(constraint_range.bit_length())

        return value

    def decode_semi_constraint_number(self, min_value):
        n_bytes = self.decode_constraint_number(0, 255)
        value = 0

        for i in range(n_bytes):
            value <<= WORD_SIZE
            value |= self.read_byte()

        value += min_value

        return value

    def decode_number(self):
        n_bytes = self.decode_constraint_number(0, 255)
        value = 0

        for i in range(n_bytes):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                value = -1

            value <<= WORD_SIZE
            value |= byte

        return value

    def decode_real(self):
        length = self.read_byte()
        if length == 0:
            return 0.0

        header = self.read_byte()
        if header == 0x40:
            return INFINITY
        if header == 0x41:
            return -INFINITY

        return self.decode_as_binary_encoding(length - 1, header)

    def decode_as_binary_encoding(self, length, header):
        if header & 0x40:
            sign = -1
        else:
            sign = 1

        if header & 0x10:
            exp_factor = 3
        elif header & 0x20:
            exp_factor = 4
        else:
            exp_factor = 1

        f = (header & 0x0c) >> 2
        factor = 1 << f
        exp_len = (header & 0x03) + 1
        n = 0
        exponent = 0

        for i in range(exp_len):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                exponent = -1

            exponent <<= WORD_SIZE
            exponent |= byte

        length -= exp_len

        for i in range(length):
            n <<= WORD_SIZE
            n |= self.read_byte()

        value = n * factor * pow(2, exp_factor * exponent)

        if sign < 0:
            value = -value

        return value


#############################
#           Types           #
#############################


class ASN1Type:
    __typing__ = 'ASN1Type'

    constraints = ''

    def get(self):
        return self

    def set(self, value):
        if isinstance(value, ASN1Type):
            value = value.get()

        if self._check_type(value) and self.check_constraints(value):
            self._set_value(value)

        else:
            if isinstance(self, ASN1SimpleType):
                expected_type = self.__base__
            elif isinstance(self, ASN1ArrayOfType):
                value = '{} elements'.format(len(value))
                expected_type = list
            else:
                expected_type = ASN1ComposedType

            raise ConstraintException(type(self).__name__, value, self.constraints, expected_type)

    def check_constraints(self, value):
        return True

    def _check_type(self, value):
        return True

    def _set_value(self, value):
        pass

    def __eq__(self, other):
        if isinstance(other, ASN1Type):
            return self.get() == other.get()

        else:
            return self.get() == other

    def __repr__(self):
        return str(self.get())

    # Encoding and decoding functions

    def encode(self, bit_stream: BitStream, encoding=None):
        if encoding == 'acn':
            return self._acn_encode(bit_stream)
        else:
            return self._uper_encode(bit_stream)

    def _acn_encode(self, bit_stream):
        return b''

    def _uper_encode(self, bit_stream):
        return b''

    def decode(self, bit_stream, encoding=None):
        if encoding == 'acn':
            return self._acn_decode(bit_stream)
        else:
            return self._uper_decode(bit_stream)

    def _acn_decode(self, bit_stream):
        pass

    def _uper_decode(self, bit_stream):
        pass


class ASN1SimpleType(ASN1Type):
    __base__ = object

    def __init__(self, source=None):
        self.set(source or self.init_value())

    def init_value(self):
        return self.__base__()

    def get(self):
        return self._value

    def _check_type(self, value):
        return isinstance(value, self.__base__)

    def _set_value(self, value):
        self._value = value


class ASN1ComposedType(ASN1Type):
    attributes = dict()
    initialized = False

    def _check_type(self, value):
        return (
            isinstance(value, ASN1ComposedType)
            and self.attributes.keys() == value.attributes.keys()
        )

    def _set_value(self, value):
        for attr in value.attributes:
            setattr(self, attr, object.__getattribute__(value, attr))
            self.attributes[attr] = value.attributes[attr]

    def __getattribute__(self, item):
        initialized = object.__getattribute__(self, 'initialized')

        if not initialized:
            return object.__getattribute__(self, item)

        attributes = object.__getattribute__(self, 'attributes')

        if item in attributes:
            if attributes[item]:
                return object.__getattribute__(self, item).get()

            else:
                raise AttributeError("Attribute {} not present!")

        else:
            return object.__getattribute__(self, item)

    def __getattr__(self, item):
        raise AttributeError("Attribute {} not exists!".format(item))

    def __setattr__(self, key, value):
        if not self.initialized:
            object.__setattr__(self, key, value)

        elif key in self.attributes:
            attribute = object.__getattribute__(self, key)

            if value is not None:
                self._set_attribute_exists(key, True)
                attribute.set(value)

            else:
                attribute_exists = False
                if isinstance(attribute, Null):
                    attribute_exists = not self.attributes[key]

                self._set_attribute_exists(key, attribute_exists)

        else:
            raise AttributeError("Can't set {} attribute!".format(key))

    def _set_attribute_exists(self, key, exists: bool):
        self.attributes[key] = exists

    def __delattr__(self, item):
        self.attributes[item] = False

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        else:
            for attr in other.attributes:
                if other.attributes[attr] != self.attributes[attr] or getattr(other, attr) != getattr(self, attr):
                    return False

            return True

    def __repr__(self):
        return str(vars(self))

    def __str__(self):
        return str({attr: str(getattr(self, attr)) for attr in self.attributes if self.attributes[attr]})


class StringWrapper:
    __wrapped__ = None
    __setter__ = None

    def __init__(self, *args):
        self.object = self.__wrapped__(*args)
        self.__wrap_methods()

    def append(self, item):
        self.__setter__(self.object + item)

    def insert(self, index, item):
        self.__setter__(self.object[:index] + item + self.object[index:])

    def remove(self, index=None):
        index = index or len(self.object)
        self.__setter__(self.object[:index] + self.object[index + 1:])

    def replace(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if key <= len(self.object):
            if hasattr(self.object, '__setitem__'):
                self.object[key] = value

            else:
                self.__setter__(self.object[:key] + value + self.object[key + 1:])
        else:
            raise AttributeError("Item {} doesn't exist!".format(key))

    def __getattr__(self, item):
        return getattr(self.object, item)

    def __wrap_methods(self):
        def make_proxy(attribute):
            def proxy(obj):
                return getattr(obj.object, attribute)

            return proxy

        ignore = {'__new__', '__mro__', '__class__', '__init__', '__getattribute__', '__dict__', '__getattr__'}
        for name in dir(self.__wrapped__):
            if name.startswith("__") and name not in ignore:
                setattr(self.__class__, name, property(make_proxy(name)))


class ASN1StringWrappedType(ASN1SimpleType):
    @staticmethod
    def _string_wrapper(wrapped, setter):
        class Wrapper(StringWrapper):
            __wrapped__ = wrapped
            __setter__ = setter

        return Wrapper

    def get(self):
        return self._value

    def _check_type(self, value):
        return super()._check_type(value) or (isinstance(value, StringWrapper) and value.__wrapped__ == self.__base__)

    def _set_value(self, value):
        self._value = self._string_wrapper(self.__base__, self.set)(value)


class ASN1ArrayOfType(ASN1Type):
    __element__ = ASN1Type

    def __init__(self, size=None):
        self._list: typing.List[self.__element__] = list()

        self.set(self._get_new_list(size or self.init_value()))

    def init_value(self):
        """:returns size of Array"""

        return 0

    def _get_new_list(self, size):
        element_list = list()

        for i in range(size):
            element_list.append(self.__element__())

        return element_list

    def get(self):
        return self._list

    def _check_type(self, value):
        return isinstance(value, list)

    def _set_value(self, value):
        self._list = list()
        for i, elem in enumerate(value):
            tmp = self.__element__()
            tmp.set(elem)
            self._list.append(tmp)

    def append(self, item):
        self._list.append(item)
        self.set(self._list)

    def remove(self, index=None):
        index = index or len(self._list)
        self.set(self._list[:index] + self._list[index + 1:])

    def replace(self, key, value):
        self[key] = value

    def __getitem__(self, item):
        if self._check_index(item):
            return self._list[item].get()

        else:
            raise AttributeError("Item {} doesn't exist!".format(item))

    def __setitem__(self, key, value):
        if self._check_index(key):
            self._list[key].set(value)

        else:
            raise AttributeError("Item {} doesn't exist!".format(key))

    def _check_index(self, index):
        return isinstance(index, int) and 0 <= index < len(self._list)

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        self._n = 0

        return self

    def __next__(self):
        if self._n < len(self._list):
            element = self._list[self._n]
            self._n += 1

            return element.get()

        else:
            raise StopIteration

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.get()

        if not isinstance(other, list):
            return False

        else:
            for i, elem in enumerate(other):
                if elem != self._list[i]:
                    return False

            return True


class Enumerated(ASN1SimpleType):
    Value = Enum

    # class Value(Enumerated.Value):
    #     NONE = None

    __base__ = Value

    def init_value(self):
        return self.Value.NONE

    def _check_type(self, value):
        return super()._check_type(value) or value in [e.value for e in self.Value]

    def _set_value(self, value):
        if not isinstance(value, self.Value):
            value = self.Value(value)

        self._value = value


class Null(ASN1SimpleType):
    def __init__(self):
        super().__init__(None)
        self._value = None

    def init_value(self):
        return None

    def set(self, value):
        if value is not None:
            raise ConstraintException(type(self).__name__, value, "Null can't be set", None)


class Integer(ASN1SimpleType):
    __base__ = int
    __typing__ = __base__

    def _uper_encode(self, bit_stream: BitStream):
        bit_stream.encode_number(self._value)

    def _uper_decode(self, bit_stream: BitStream):
        self._value = bit_stream.decode_number()


class Real(ASN1SimpleType):
    __base__ = float
    __typing__ = __base__

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)

    def _uper_encode(self, bit_stream: BitStream):
        bit_stream.encode_real(self._value)

    def _uper_decode(self, bit_stream: BitStream):
        self._value = bit_stream.decode_real()


class Boolean(ASN1SimpleType):
    __base__ = bool
    __typing__ = __base__

    def _check_type(self, value):
        return isinstance(bool(value), bool)

    def _set_value(self, value):
        self._value = bool(value)


class BitString(ASN1StringWrappedType):
    __base__ = bitarray
    __typing__ = typing.Union['BitString', StringWrapper, __base__]

    def set(self, value):
        if isinstance(value, bytes):
            value = bitarray(value)

        super().set(value)

    def _check_type(self, value):
        return hasattr(value, '__iter__') and all([is_bit(c) for c in value])


class OctetString(ASN1StringWrappedType):
    __base__ = bytearray
    __typing__ = typing.Union['OctetString', StringWrapper, __base__]

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, bytes)


class IA5String(ASN1StringWrappedType):
    __base__ = str
    __typing__ = typing.Union['IA5String', StringWrapper, __base__]


class NumericString(ASN1StringWrappedType):
    __base__ = str
    __typing__ = typing.Union['NumericString', StringWrapper, __base__]

    def _check_type(self, value):
        return super()._check_type(value) and str(value).isdigit()


class Sequence(ASN1ComposedType):
    _optional = list()

    def _init_from_source(self, source):
        if not source:  # default initialization
            return

        for attribute in self.attributes:
            self.attributes[attribute] = False
            value = source.get(attribute, None)
            setattr(self, attribute, value)

    def _set_attribute_exists(self, key, exists: bool):
        if not exists and key not in self._optional:
            raise AttributeError("Attribute {} of {} object can't be Optional!".format(key, type(self).__name__))

        self.attributes[key] = exists


class Set(Sequence):
    pass


class Choice(ASN1ComposedType):
    def _init_choice(self, choice):
        if choice:
            attribute = object.__getattribute__(self, choice['name'])
            setattr(self, choice['name'], attribute.__class__(choice['value']))

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        self._set_choice(key)

    def _set_choice(self, key):
        for choice in self.attributes:
            self.attributes[choice] = False

            if choice == key:
                self.attributes[choice] = True


class SequenceOf(ASN1ArrayOfType):
    pass


class SetOf(ASN1ArrayOfType):
    pass
