from enum import Enum

import typing

#############################
#           Bits            #
#############################

WORD_SIZE = 8


class bitarray:
    def __init__(self, source=None):
        self._data = bytearray()
        self._bitsize = 0

        if isinstance(source, int):
            self.__init_from_size(source)

        elif self.__expandable(source):
            self.__append_from_iterable(source)

        elif isinstance(source, bytearray) or isinstance(source, bytes):
            self.__init_from_bytes(source)

    def __init_from_size(self, size):
        self._data = bytearray((size + WORD_SIZE - 1) // WORD_SIZE)
        self._bitsize = size

    def __append_from_iterable(self, source):
        for c in source:
            self._append(int(c))

    def __init_from_bytes(self, source):
        self._data = bytearray(source)
        self._bitsize = len(self._data) * WORD_SIZE

    def __getitem__(self, item):
        if isinstance(item, slice):
            return bitarray([self[i] for i in range(item.start or 0, item.stop or self._bitsize, item.step or 1)])

        self.__assert_correct_index(item)

        bit_position = self.__get_bit_position(item)
        byte_position = self.__get_byte_position(item)

        byte = self._data[byte_position]
        byte &= (0b00000001 << bit_position)

        return byte >> bit_position

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
        if self.__expandable(other):
            self.__append_from_iterable(other)
        elif is_bit(other):
            self._append(int(other))
        else:
            raise AttributeError("Bit can be 0 1 only!")

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
        self._append(bit)

    def _append(self, bit):
        self.__assert_bit(bit)
        if self._bitsize % WORD_SIZE:
            byte = self._data.pop()
        else:
            byte = 0b00000000

        bit_position = self.__get_bit_position(self._bitsize)
        byte = self.__set_bit(byte, bit_position) if bit else self.__clear_bit(byte, bit_position)

        self._bitsize += 1
        self._data.append(byte)

    def clear(self):
        self._data = bytearray()
        self._bitsize = 0

    def bytes(self):
        return self._data

    def copy(self):
        return bitarray(self)

    def extend(self, other):
        if self.__expandable(other):
            self.__append_from_iterable(other)

    @staticmethod
    def __expandable(source):
        return hasattr(source, '__iter__') and all([is_bit(c) for c in source])

    @classmethod
    def fromhex(cls, s):
        return bitarray(bytearray.fromhex(s))

    def hex(self):
        return self._data.hex()

    def insert(self, index, value):
        self.__assert_correct_index(index)
        self.__assert_bit(value)

        self._append(0)
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

    def __assert_correct_index(self, index):
        if 0 <= index >= self._bitsize:
            raise AttributeError("Not existing item!")

    @staticmethod
    def __assert_bit(bit):
        if not is_bit(bit):
            raise AttributeError("Bit can be 0 1 only!")

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


def get_min_bytes_to_store_bits(n_bits):
    return (n_bits + WORD_SIZE + 1) // WORD_SIZE


def get_max_bits_stored(n_bytes):
    return n_bytes * WORD_SIZE


#############################
#    Encoding / Decoding    #
#############################


class BitStream:
    def __init__(self, buffer=None):
        self.buffer = buffer or list()
        self.current_byte = 0
        self.current_bit = 0

    @staticmethod
    def __assert_bit(bit):
        if is_bit(bit):
            return True
        else:
            raise Exception("Not bit!")

    def append(self, bit):
        self.__assert_bit(bit)

        self.buffer.append(int(bit))

    def push(self, bit):
        self.append(bit)

    def pop(self, index=None):
        self.buffer.pop(index)

    def __getitem__(self, item):
        return self.buffer[item]

    def __setitem__(self, key, value):
        self.__assert_bit(value)

        self.buffer[key] = value

    def __str__(self):
        return ''.join(self.buffer)

    def to_hex(self):
        pass


#############################
#           Types           #
#############################


class ASN1Type:
    __checktype__ = None

    def get(self):
        return self

    def set(self, value):
        if isinstance(value, self.__class__):
            value = value.get()

        if self._check_type(value) and self.check_constraints(value):
            self._set_value(value)
        else:
            raise Exception("Constraint failed! {} object cannot be {}".format(type(self).__name__, value))

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

    def encode(self, encoding='acn'):
        if encoding == 'acn':
            return self._acn_encode()
        else:
            return b''

    def _acn_encode(self):
        return b''

    def decode(self, source, encoding='acn'):
        if encoding == 'acn':
            return self._acn_decode(source)
        else:
            pass

    def _acn_decode(self, source):
        pass


class ASN1SimpleType(ASN1Type):
    simple_type = object

    def __init__(self, source=None):
        self.set(source or self.init_value())

    def init_value(self):
        return self.simple_type()

    def get(self):
        return self._value

    def _check_type(self, value):
        return isinstance(value, self.simple_type)

    def _set_value(self, value):
        self._value = value


class ASN1ComposedType(ASN1Type):
    attributes = dict()
    initialized = False

    def _check_type(self, value):
        return isinstance(value, self.__class__)

    def _set_value(self, value):
        for attr, val in vars(value).items():
            getattr(self, attr).set(val)

    def __getattribute__(self, item):
        initialized = object.__getattribute__(self, 'initialized')

        if not initialized:
            return object.__getattribute__(self, item)

        attributes = object.__getattribute__(self, 'attributes')
        if item in attributes:
            if attributes[item]:
                return object.__getattribute__(self, item).get()
            else:
                raise Exception("Attribute {} not present!")
        else:
            return object.__getattribute__(self, item)

    def __getattr__(self, item):
        raise Exception("Attribute {} not exists!".format(item))

    def __setattr__(self, key, value):
        if not self.initialized:
            object.__setattr__(self, key, value)

        else:
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
            else:
                return True

    def __repr__(self):
        return str(vars(self))


class StringWrapper:
    __cls__ = None
    __setter__ = None

    def __init__(self, *args):
        self.wrapped = self.__cls__(*args)
        self.__wrap_methods()

    def append(self, item):
        self.__setter__(self.wrapped + item)

    def insert(self, index, item):
        self.__setter__(self.wrapped[:index] + item + self.wrapped[index:])

    def remove(self, index=None):
        index = index or len(self.wrapped)
        self.__setter__(self.wrapped[:index] + self.wrapped[index + 1:])

    def replace(self, key, value):
        self[key] = value

    def __setitem__(self, key, value):
        if key <= len(self.wrapped):
            if hasattr(self.wrapped, '__setitem__'):
                self.wrapped[key] = value
            else:
                self.__setter__(self.wrapped[:key] + value + self.wrapped[key + 1:])
        else:
            raise Exception("{} index out of range".format(self.__cls__.__name__))

    def __getattr__(self, item):
        return getattr(self.wrapped, item)

    def __wrap_methods(self):
        def make_proxy(attribute):
            def proxy(obj):
                return getattr(obj.wrapped, attribute)

            return proxy

        ignore = {'__new__', '__mro__', '__class__', '__init__', '__getattribute__', '__dict__', '__getattr__'}
        for name in dir(self.__cls__):
            if name.startswith("__") and name not in ignore:
                setattr(self.__class__, name, property(make_proxy(name)))


class ASN1StringWrappedType(ASN1SimpleType):
    @staticmethod
    def string_wrapper(cls, setter):
        class Wrapper(StringWrapper):
            __cls__ = cls
            __setter__ = setter

        return Wrapper

    def _set_value(self, value):
        self._value = self.string_wrapper(self.simple_type, self.set)(value)


class ASN1ArrayOfType(ASN1Type):
    max_size = 0
    element_type = ASN1Type

    def __init__(self):
        self.list: typing.List[self.element_type] = list()
        self._init_list()

    def _init_list(self):
        for i in range(self.max_size):
            self.list.append(self.element_type())

    def get(self):
        return self.list

    def _check_type(self, value):
        return isinstance(value, list)

    def _set_value(self, value):
        for i, elem in enumerate(value):
            self.list[i].set(elem)

    def __getitem__(self, item):
        if self._check_index(item):
            return self.list[item].get()

        else:
            raise Exception("Max size of {} is {}".format(type(self).__name__, len(self)))

    def __setitem__(self, key, value):
        if self._check_index(key):
            self.list[key].set(value)

        else:
            raise Exception("Max size of {} is {}".format(type(self).__name__, len(self)))

    def _check_index(self, index):
        return isinstance(index, int) and len(self.list) > index

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        self._n = 0

        return self

    def __next__(self):
        if self._n < len(self.list):
            element = self.list[self._n]
            self._n += 1

            return element.get()

        else:
            del self._n
            raise StopIteration

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.get()

        if not isinstance(other, list):
            return False

        else:
            for i, elem in enumerate(other):
                if elem != self.list[i]:
                    return False
            else:
                return True


class Enumerated(ASN1SimpleType):

    Value = Enum
    __checktype__ = 'Value'

    # class Value(Value):
    #     NONE = None

    simple_type = Value

    def init_value(self):
        return self.Value.NONE


class Null(ASN1SimpleType):
    def __init__(self):
        super().__init__()

        self._value = None

    def set(self, value):
        raise Exception("Constraint failed! {} object cannot be changed".format(type(self).__name__))


class Integer(ASN1SimpleType):
    simple_type = int
    __checktype__ = simple_type


class Real(ASN1SimpleType):
    simple_type = float
    __checktype__ = simple_type

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)


class Boolean(ASN1SimpleType):
    simple_type = bool
    __checktype__ = simple_type

    def _check_type(self, value):
        return isinstance(bool(value), bool)

    def _set_value(self, value):
        self._value = bool(value)


class BitString(ASN1StringWrappedType):
    simple_type = bitarray
    __checktype__ = typing.Union['BitString', StringWrapper, simple_type]

    def _check_type(self, value):
        return hasattr(value, '__iter__') and all([is_bit(c) for c in value])


class OctetString(ASN1StringWrappedType):
    simple_type = bytearray
    __checktype__ = typing.Union['OctetString', StringWrapper, simple_type]

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, bytes)


class IA5String(ASN1StringWrappedType):
    simple_type = str
    __checktype__ = typing.Union['IA5String', StringWrapper, simple_type]


class NumericString(ASN1StringWrappedType):
    simple_type = str
    __checktype__ = typing.Union['NumericString', StringWrapper, simple_type]

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
