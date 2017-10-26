from enum import Enum

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
    @property
    def val(self):
        return self.get()

    @val.setter
    def val(self, value):
        self.set(value)

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
        self._value = self.simple_type()

    def get(self):
        return self._value

    def _check_type(self, value):
        return isinstance(value, self.simple_type)

    def _set_value(self, value):
        self._value = value


class ASN1ComposedType(ASN1Type):
    attributes = list()

    def _check_type(self, value):
        return isinstance(value, self.__class__)

    def _set_value(self, value):
        for attr, val in vars(value).items():
            getattr(self, attr).set(val)

    def __getattribute__(self, item):
        attributes = object.__getattribute__(self, 'attributes')
        attribute = object.__getattribute__(self, item)

        if attribute in attributes:
            return attribute.get()
        else:
            raise Exception("Attribute {} not exists!".format(item))

    def __setattr__(self, key, value):
        attribute = object.__getattribute__(self, key)

        attribute.set(value)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        else:
            for attr, val in vars(other).items():
                if val != getattr(self, attr):
                    return False
            else:
                return True

    def __repr__(self):
        return str(vars(self))


class ASN1ArrayOfType(ASN1Type):
    max_size = 0
    element_type = object

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
            return self.list[item]

        else:
            raise Exception("Max size of {} is {}".format(type(self).__name__, len(self)))

    def __setitem__(self, key, value):
        if self._check_index(key):
            self.list[key] = value

        else:
            raise Exception("Max size of {} is {}".format(type(self).__name__, len(self)))

    def _check_index(self, index):
        return isinstance(index, int) and len(self) > index

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        self._n = 0

        return self

    def __next__(self):
        if self._n < len(self):
            element = self[self._n]
            self._n += 1

            return element

        else:
            del self._n
            raise StopIteration

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other = other.val

        if not isinstance(other, list):
            return False

        else:
            for i, elem in enumerate(other):
                if elem != self[i]:
                    return False
            else:
                return True


class Enumerated(Enum):
    @property
    def val(self):
        return self.value


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
    def __getattribute__(self, item):
        exists = object.__getattribute__(self, 'exists')
        if item in exists:
            self._set_choice(item)

        return object.__getattribute__(self, item)

    def _set_choice(self, item):
        for choice in self.exists:
            self.exists[choice] = False
        self.exists[item] = True


class SequenceOf(ASN1ArrayOfType):
    pass


class SetOf(ASN1ArrayOfType):
    pass
