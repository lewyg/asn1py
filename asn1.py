from enum import Enum


#############################
#         bitarray          #
#############################

class bitarray:
    BITS_IN_BYTE = 8

    def __init__(self, source=0):
        if isinstance(source, int):
            self._data = bytearray((source + self.BITS_IN_BYTE - 1) // self.BITS_IN_BYTE)
            self._bitsize = source
        else:
            self._data = bytearray(source)
            self._bitsize = len(self._data)

    def __getitem__(self, item):
        bit_position = self.__get_bit_position(item)
        byte_position = self.__get_byte_position(item)
        byte = self._data[byte_position]
        byte &= (0b00000001 << bit_position)

        return byte >> bit_position

    def __setitem__(self, item, value):
        bit_position = self.__get_bit_position(item)
        byte_position = self.__get_byte_position(item)
        byte = self._data[byte_position]
        byte = self.__set_bit(byte, bit_position) if value else self.__clear_bit(byte, bit_position)
        self._data[byte_position] = byte

    def __add__(self, *args, **kwargs):  # real signature unknown
        """ Return self+value. """
        pass

    def __delitem__(self, *args, **kwargs):  # real signature unknown
        """ Delete self[key]. """
        pass

    def __eq__(self, *args, **kwargs):  # real signature unknown
        """ Return self==value. """
        pass

    def __iadd__(self, *args, **kwargs):  # real signature unknown
        """ Implement self+=value. """
        pass

    def __imul__(self, *args, **kwargs):  # real signature unknown
        """ Implement self*=value. """
        pass

    def __iter__(self, *args, **kwargs):  # real signature unknown
        self._n = 0
        return self

    def __next__(self):
        if self._n < self._bitsize:
            element = self[self._n]
            self._n += 1
            return element

        else:
            raise StopIteration

    def __len__(self, *args, **kwargs):  # real signature unknown
        return self._bitsize

    def __mul__(self, *args, **kwargs):  # real signature unknown
        """ Return self*value.n """
        pass

    def __ne__(self, *args, **kwargs):  # real signature unknown
        """ Return self!=value. """
        pass

    def __repr__(self, *args, **kwargs):
        return ''.join([str(bit) for bit in self])

    def __sizeof__(self):
        return self._data.__sizeof__()

    def append(self, bit):
        if self._bitsize % self.BITS_IN_BYTE:
            byte = self._data.pop()
        else:
            byte = 0b00000000

        bit_position = self.__get_bit_position(self._bitsize)
        byte = self.__set_bit(byte, bit_position) if bit else self.__clear_bit(byte, bit_position)

        self._bitsize += 1
        self._data.append(byte)

    def clear(self, *args, **kwargs):  # real signature unknown
        self._data = bytearray()
        self._bitsize = 0

    def copy(self, *args, **kwargs):  # real signature unknown
        """ Return a copy of B. """
        pass

    def extend(self, *args, **kwargs):  # real signature unknown
        """
        Append all the items from the iterator or sequence to the end of the bytearray.

          iterable_of_ints
            The iterable of items to append.
        """
        pass

    @classmethod  # known case
    def fromhex(cls, *args, **kwargs):  # real signature unknown; NOTE: unreliably restored from __doc__
        """
        Create a bytearray object from a string of hexadecimal numbers.

        Spaces between two numbers are accepted.
        Example: bytearray.fromhex('B9 01EF') -> bytearray(b'\\xb9\\x01\\xef')
        """
        pass

    def hex(self):  # real signature unknown; restored from __doc__
        """
        B.hex() -> string

        Create a string of hexadecimal numbers from a bytearray object.
        Example: bytearray([0xb9, 0x01, 0xef]).hex() -> 'b901ef'.
        """
        return ""

    def insert(self, *args, **kwargs):  # real signature unknown
        """
        Insert a single item into the bytearray before the given index.

          index
            The index where the value is to be inserted.
          item
            The item to be inserted.
        """
        pass

    def join(self, *args, **kwargs):  # real signature unknown
        """
        Concatenate any number of bytes/bytearray objects.

        The bytearray whose method is called is inserted in between each pair.

        The result is returned as a new bytearray object.
        """
        pass

    def pop(self, *args, **kwargs):  # real signature unknown
        """
        Remove and return a single item from B.

          index
            The index from where to remove the item.
            -1 (the default value) means remove the last item.

        If no index argument is given, will pop the last item.
        """
        pass

    def reverse(self, *args, **kwargs):  # real signature unknown
        """ Reverse the order of the values in B in place. """
        pass

    @staticmethod
    def __set_bit(byte, bit):
        return byte | (1 << bit)

    @staticmethod
    def __clear_bit(byte, bit):
        return byte & ~(1 << bit)

    def __get_byte_position(self, position):
        return position // self.BITS_IN_BYTE

    def __get_bit_position(self, position):
        return self.BITS_IN_BYTE - position % self.BITS_IN_BYTE - 1


#############################
#    Encoding / Decoding    #
#############################

WORD_SIZE = 8


class BitStream:
    def __init__(self, buffer=None):
        self.buffer = buffer or list()
        self.current_byte = 0
        self.current_bit = 0

    @staticmethod
    def __assert_bit(bit):
        if str(bit) in "01":
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


def get_min_bytes_to_store_bits(n_bits):
    return (n_bits + WORD_SIZE + 1) // WORD_SIZE


def get_max_bits_stored(n_bytes):
    return n_bytes * WORD_SIZE


#############################
#           Types           #
#############################

class ASN1Type:
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

    def decode(self, bytes, encoding='acn'):
        if encoding == 'acn':
            return self._acn_decode(bytes)
        else:
            pass

    def _acn_decode(self, bytes):
        pass


class ASN1SimpleType(ASN1Type):
    simple_type = object

    def __init__(self):
        self._value = self.init_value()

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


class ASN1ArrayOfType(ASN1Type):
    max_size = 0
    element_type = ASN1Type

    def __init__(self):
        self.list = list()
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

            return element

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


EnumElement = Enum


class Enumerated(ASN1SimpleType):
    Value = Enum

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


class Real(ASN1SimpleType):
    simple_type = float

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)


class Boolean(ASN1SimpleType):
    simple_type = bool

    def _check_type(self, value):
        return bool(value)

    def _set_value(self, value):
        self._value = bool(value)


class BitString(ASN1SimpleType):
    simple_type = list

    def _check_type(self, value):
        return hasattr(value, '__iter__') and all([str(c) in '01' for c in value])

    def _set_value(self, value):
        self._value = list()
        for i in value:
            self._value.append(int(i))


class OctetString(ASN1SimpleType):
    simple_type = bytearray


class IA5String(ASN1SimpleType):
    simple_type = str


class NumericString(ASN1SimpleType):
    simple_type = str

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
