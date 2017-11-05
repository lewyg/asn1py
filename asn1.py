from enum import Enum

import typing


#############################
#        Exceptions         #
#############################

class ASN1Erorr(Exception):
    pass


class ConstraintException(ASN1Erorr):
    def __init__(self, class_name, constraints, value):
        message = "Constraint failed! {} object can't be {} ( {} )".format(class_name, value, constraints)
        super().__init__(message)


#############################
#           Bits            #
#############################

WORD_SIZE = 8


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
        self._data = bytearray(get_byte_size_from_bit_size(size))
        self._bitsize = size

    def _init_from_iterable(self, source):
        self.__append_bits(source)

    def _init_from_bytes(self, source):
        self._data = bytearray(source)
        self._bitsize = get_bit_size_from_byte_size(len(self._data))

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


def get_byte_size_from_bit_size(bit_size):
    return (bit_size + WORD_SIZE + 1) // WORD_SIZE


def get_bit_size_from_byte_size(byte_size):
    return byte_size * WORD_SIZE


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

    def _negate_byte(self, value):
        return (1 << WORD_SIZE) - 1 - value

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
            byte = self._negate_byte(byte)

        self._buffer.append_byte(byte)
        self._current_byte += 1

    def append_byte_one(self):
        self._buffer.append_byte(0b11111111)

    def append_byte_zero(self):
        self._buffer.append_byte(0b00000000)

    def append_partial_byte(self, byte, n_bits, negate=False):
        if negate:
            byte = self._negate_byte(byte)

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

            self.encode_non_negative_integer32(hi,  negate)
            lo_bits = lo.bit_length()
            self.append_bits_zero(32 - lo_bits)
            self.encode_non_negative_integer32(lo,  negate)



#############################
#           Types           #
#############################


class ASN1Type:
    __typing__ = None

    constraints = ''

    def get(self):
        return self

    def set(self, value):
        if isinstance(value, self.__class__):
            value = value.get()

        if self._check_type(value) and self.check_constraints(value):
            self._set_value(value)

        else:
            raise ConstraintException(self.__class__.__name__, self.constraints, value)

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

    def encode(self, bit_stream, encoding='acn'):
        if encoding == 'acn':
            return self._acn_encode(bit_stream)
        else:
            return b''

    def _acn_encode(self, bit_stream):
        return b''

    def decode(self, bit_stream, encoding='acn'):
        if encoding == 'acn':
            return self._acn_decode(bit_stream)
        else:
            pass

    def _acn_decode(self, bit_stream):
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
        return isinstance(value, self.__class__)

    def _set_value(self, value):
        for attr, val in vars(value).items():
            setattr(self, attr, val)

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

        else:
            if key in self.attributes:
                self.attributes[key] = True
            attribute = object.__getattribute__(self, key)

            if isinstance(attribute, ASN1Type):
                attribute.set(value)

            else:
                object.__setattr__(self, key, value)

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


class Null(ASN1SimpleType):
    def __init__(self):
        super().__init__()

        self._value = None

    def set(self, value):
        raise ConstraintException(self.__class__.__name__, value, "Null can't be set")


class Integer(ASN1SimpleType):
    __base__ = int
    __typing__ = __base__


class Real(ASN1SimpleType):
    __base__ = float
    __typing__ = __base__

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)


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
    pass


class Set(ASN1ComposedType):
    pass


class Choice(ASN1ComposedType):
    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        for choice in self.attributes:
            self.attributes[choice] = False

            if choice == key:
                self.attributes[choice] = True


class SequenceOf(ASN1ArrayOfType):
    pass


class SetOf(ASN1ArrayOfType):
    pass
