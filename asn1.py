import json
import struct
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

class ASN1Error(Exception):
    pass


class ConstraintException(ASN1Error):
    def __init__(self, class_name, value, constraints, expected_type):
        message = "Constraint failed! {} object can't be {} ( {} - {} )".format(
            class_name, value, constraints, expected_type
        )
        super().__init__(message)


class UnexpectedOption(ASN1Error):
    def __init__(self, cls, option):
        message = "Unexpected option {} for type {}".format(option, cls.__name__)
        super().__init__(message)


class UnexpectedValueException(ASN1Error):
    def __init__(self, cls, value):
        message = "Unexpected value {} for {}".format(value, cls.__name__)
        super().__init__(message)


class UnexpectedOptionIndex(ASN1Error):
    def __init__(self, cls, option):
        message = "Unexpected option index {} for type {}".format(option, cls.__name__)
        super().__init__(message)


class NotImplementedEncoding(ASN1Error):
    def __init__(self, encoding):
        message = "Not implemented encoding, decoding method for {}".format(encoding)
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

        elif isinstance(source, bytearray) or isinstance(source, bytes):
            self._init_from_bytes(source)

        elif self.__iterable_bits(source):
            self._init_from_iterable(source)

    def _init_from_size(self, size):
        self._data = bytearray(get_byte_length_from_bit_length(size))
        self._bitsize = size

    def _init_from_iterable(self, source):
        self.__append_bits(source)

    def _init_from_bytes(self, source):
        self._data = bytearray(source)
        self._bitsize = len(self._data) * WORD_SIZE

    def set_size(self, new_size):
        self._bitsize = new_size

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
        byte = self.__set_bit(byte, bit_position) if int(value) else self.__clear_bit(byte, bit_position)
        self._data[byte_position] = byte

    def __delitem__(self, item):
        self.__assert_correct_index(item)

        for i in range(item, self._bitsize - 1):
            self[i] = self[i + 1]

        self[self._bitsize - 1] = 0
        self._bitsize -= 1

    def __add__(self, other):
        if is_bit(other):
            self.append_bit(int(other))

        elif isinstance(other, bytes):
            for byte in other:
                self.append_byte(byte)

        elif self.__iterable_bits(other):
            self.__append_bits(other)

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
        self.append_bit(bit)

    def append_bit(self, bit):
        self.__assert_bit(bit)

        if self._bitsize % WORD_SIZE:
            byte = self._data.pop()
        else:
            byte = 0b00000000

        bit_position = self.__get_bit_position(self._bitsize)
        byte = self.__set_bit(byte, bit_position) if int(bit) else self.__clear_bit(byte, bit_position)

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

        self.append_bit(0)

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
            self.append_bit(int(c))

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
    return str(int(c)) in ['0', '1']


def get_byte_length_from_bit_length(bit_length):
    return (bit_length + WORD_SIZE - 1) // WORD_SIZE


def negate_byte(value):
    return (1 << WORD_SIZE) - 1 - value


def get_signed_int_byte_length(value: int):
    bit_length = get_signed_int_bit_length(value)

    return get_byte_length_from_bit_length(bit_length) or 1


def get_signed_int_bit_length(value: int):
    if value >= 0:
        bit_length = value.bit_length()
    else:
        bit_length = int(~value).bit_length()

    if bit_length:
        bit_length += 1  # one bit for mark sign

    return bit_length


def int_to_uint(value):
    return value


def uint_to_int(value, uint_size_in_bytes=4):
    return value - (value >> (uint_size_in_bytes * WORD_SIZE) - 1) * (1 << (uint_size_in_bytes * WORD_SIZE))


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

    def from_file(self, filename):
        file = open(filename, "rb")
        self._buffer = bitarray(file.read())
        self._current_byte = 0
        self._current_bit = 0

    def to_file(self, filename):
        file = open(filename, "wb")
        file.write(self._buffer.bytes())

    def __len__(self):
        return len(self._buffer)

    def __str__(self):
        return str(self._buffer)

    def _get_current_position(self):
        return self._current_byte * WORD_SIZE + self._current_bit

    def _increment_bit_counter(self):
        self._current_bit += 1
        if self._current_bit == WORD_SIZE:
            self._current_bit = 0
            self._current_byte += 1

    def _align_to_next_byte(self):
        self.append_bits_zero(self._current_bit & WORD_SIZE)

    def _align_to_next_word(self):
        self.__align_to_n_bytes(2)

    def _align_to_next_dword(self):
        self.__align_to_n_bytes(4)

    def __align_to_n_bytes(self, n_bytes):
        self._align_to_next_byte()
        while self._current_byte % n_bytes:
            self.append_byte_one()

    def _requires_reverse(self):
        return sys.byteorder == 'little'

    # append methods

    def append_bit(self, bit):
        self._buffer.append_bit(bit)
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
        if isinstance(source, bitarray):
            source = source.bytes()

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
            byte <<= 1

    # read functions

    def read_bit(self):
        bit = self._buffer[self._get_current_position()]
        self._increment_bit_counter()

        return bit

    def read_byte(self):
        position = self._get_current_position()
        byte = int(str(self._buffer[position:position + WORD_SIZE]), 2)
        self._current_byte += 1

        return byte

    def read_bits(self, n_bits):
        result = bytearray()

        for i in range(n_bits // WORD_SIZE):
            result.append(self.read_byte())

        if n_bits % WORD_SIZE:
            result.append(self.read_partial_byte(n_bits % WORD_SIZE))

        return result

    def read_bitarray(self, size):
        result = bitarray(self.read_bits(size))
        result.set_size(size)

        return result

    def read_partial_byte(self, n_bits):
        byte = 0
        for i in range(n_bits):
            bit = self.read_bit()
            byte |= bit << (WORD_SIZE - i - 1)

        return byte

    def read_bit_pattern(self, pattern, n_bits):
        value = True
        n_bytes = n_bits // WORD_SIZE
        rest_bits = n_bits % WORD_SIZE

        for i in range(n_bytes):
            byte = self.read_byte()
            if byte != pattern[i]:
                value = False

        if rest_bits:
            byte = self.read_partial_byte(rest_bits)
            if byte != pattern[n_bytes] & 0xFF << (WORD_SIZE - rest_bits):
                value = False

        return value

    ############
    #   uPER   #
    ############

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
        assert min_value <= value <= max_value

        range_bit_length = int(max_value - min_value).bit_length()
        value_bit_length = (value - min_value).bit_length()
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
            self.append_bits_one(value_byte_length * WORD_SIZE - (~value).bit_length())
            self.encode_non_negative_integer((~value), True)

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

        if exponent >= 0:
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
            value |= self.read_partial_byte(n_bits) >> (WORD_SIZE - n_bits)

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
            value += self.decode_non_negative_integer(constraint_range.bit_length())

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

    ############
    #   uPER   #
    ############

    def acn_get_integer_size_bcd(self, value):
        result = 0
        while value > 0:
            value //= 10
            result += 1

        return result  # len(str(value))

    def acn_get_integer_size_ascii(self, value):
        if value < 0:
            value = -value

        return self.acn_get_integer_size_bcd(value) + 1

    # encoding

    def acn_encode_positive_integer_const_size(self, value, encoded_size_in_bits):
        if encoded_size_in_bits == 0:
            return

        n_bits = value.bit_length()
        self.append_bits_zero(encoded_size_in_bits - n_bits)
        self.encode_non_negative_integer(value)

    def acn_encode_positive_integer_const_size_byte(self, value, n_bytes, byteorder):
        if byteorder == 'little':
            self._acn_encode_positive_integer_const_size_little_endian(value, n_bytes)
        elif byteorder == 'big':
            self._acn_encode_positive_integer_const_size_big_endian(value, n_bytes)

    def _acn_encode_positive_integer_const_size_big_endian(self, value, n_bytes):
        mask = 0xFF << ((n_bytes - 1) * WORD_SIZE)
        for i in range(n_bytes):
            byte = (value & mask) >> ((n_bytes - i - 1) * WORD_SIZE)
            self.append_byte(byte)
            mask >>= WORD_SIZE

    def _acn_encode_positive_integer_const_size_little_endian(self, value, n_bytes):
        for i in range(n_bytes):
            byte = value & 0xFF
            self.append_byte(byte)
            value >>= WORD_SIZE

    def acn_encode_positive_integer_const_size_8(self, value):
        self.append_byte(value & 0xFF)

    def acn_encode_positive_integer_const_size_16(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_byte(value, 2, byteorder)

    def acn_encode_positive_integer_const_size_32(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_byte(value, 4, byteorder)

    def acn_encode_positive_integer_const_size_64(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_byte(value, 8, byteorder)

    def _acn_encode_unsigned_integer(self, value, n_bytes):
        int_size = 8
        assert n_bytes <= int_size

        max_byte_mask = 0xFF00000000000000

        value <<= ((int_size - n_bytes) * WORD_SIZE)
        for i in range(n_bytes):
            byte = (value & max_byte_mask) >> ((int_size - 1) * WORD_SIZE)
            self.append_byte(byte)
            value <<= WORD_SIZE

    def acn_encode_positive_integer_var_size_length_embedded(self, value):
        n_bytes = get_byte_length_from_bit_length(value.bit_length())

        self.append_byte(n_bytes)
        self._acn_encode_unsigned_integer(value, n_bytes)

    def acn_encode_integer_twos_complement_const_size(self, value, encoded_size_in_bits):
        bit_length = get_signed_int_bit_length(value)
        assert bit_length <= encoded_size_in_bits

        if value >= 0:
            self.append_bits_zero(encoded_size_in_bits - value.bit_length())
            self.encode_non_negative_integer(value)

        else:
            self.append_bits_one(encoded_size_in_bits - (~value).bit_length())
            self.encode_non_negative_integer(~value, True)

    def acn_encode_integer_twos_complement_const_size_8(self, value):
        assert get_signed_int_bit_length(value) <= 8
        self.acn_encode_positive_integer_const_size_8(int_to_uint(value))

    def acn_encode_integer_twos_complement_const_size_16(self, value, byteorder):
        assert get_signed_int_bit_length(value) <= 16
        self.acn_encode_positive_integer_const_size_16(int_to_uint(value), byteorder)

    def acn_encode_integer_twos_complement_const_size_32(self, value, byteorder):
        assert get_signed_int_bit_length(value) <= 32
        self.acn_encode_positive_integer_const_size_32(int_to_uint(value), byteorder)

    def acn_encode_integer_twos_complement_const_size_64(self, value, byteorder):
        assert get_signed_int_bit_length(value) <= 64
        self.acn_encode_positive_integer_const_size_64(int_to_uint(value), byteorder)

    def acn_encode_integer_twos_complement_var_size_length_embedded(self, value):
        n_bytes = get_signed_int_byte_length(value)

        self.append_byte(n_bytes)
        self._acn_encode_unsigned_integer(int_to_uint(value), n_bytes)

    def acn_encode_integer_bcd_const_size(self, value, encoded_size_in_nibbles):
        assert encoded_size_in_nibbles <= 100

        digits = list()
        while value > 0:
            digits.append(value % 10)
            value //= 10

        assert len(digits) <= encoded_size_in_nibbles

        for digit in reversed(digits):
            self.append_partial_byte((digit & 0xF) << 4, 4)

    def acn_encode_integer_bcd_var_size_length_embedded(self, value):
        n_nibbles = self.acn_get_integer_size_bcd(value)
        self.append_byte(n_nibbles & 0xFFFFFFFF)
        self.acn_encode_integer_bcd_const_size(value, n_nibbles)

    def acn_encode_integer_bcd_var_size_null_terminated(self, value):
        n_nibbles = self.acn_get_integer_size_bcd(value)
        self.acn_encode_integer_bcd_const_size(value, n_nibbles)
        self.append_partial_byte(0xF << 4, 4)

    def acn_encode_unsigned_integer_ascii_const_size(self, value, encoded_size_in_bytes):
        assert encoded_size_in_bytes <= 100

        digits = list()
        while value > 0:
            digits.append(value % 10)
            value //= 10

        assert len(digits) <= encoded_size_in_bytes

        for digit in reversed(digits):
            self.append_byte(digit + ord('0'))

    def acn_encode_signed_integer_ascii_const_size(self, value, encoded_size_in_bytes):
        if value < 0:
            value = -value
            sign = '-'
        else:
            sign = '+'

        self.append_byte(ord(sign))
        self.acn_encode_unsigned_integer_ascii_const_size(value, encoded_size_in_bytes - 1)

    def acn_encode_unsigned_integer_ascii_var_size_length_embedded(self, value):
        n_chars = self.acn_get_integer_size_bcd(value)
        self.append_byte(n_chars)
        self.acn_encode_unsigned_integer_ascii_const_size(value, n_chars)

    def acn_encode_signed_integer_ascii_var_size_length_embedded(self, value):
        n_chars = self.acn_get_integer_size_ascii(value)
        self.append_byte(n_chars)
        self.acn_encode_signed_integer_ascii_const_size(value, n_chars)

    def acn_encode_unsigned_integer_ascii_var_size_null_terminated(self, value):
        n_chars = self.acn_get_integer_size_bcd(value)
        self.acn_encode_unsigned_integer_ascii_const_size(value, n_chars)
        self.append_byte(0)

    def acn_encode_signed_integer_ascii_var_size_null_terminated(self, value):
        n_chars = self.acn_get_integer_size_ascii(value)
        self.acn_encode_signed_integer_ascii_const_size(value, n_chars)
        self.append_byte(0)

    def acn_encode_real_big_endian(self, value: float, format_type='f'):
        value_bytes = bytearray(struct.pack(format_type, value))

        if self._requires_reverse():
            value_bytes = reversed(value_bytes)

        for byte in value_bytes:
            self.append_byte(byte)

    def acn_encode_real_ieee745_32_big_endian(self, value):
        self.acn_encode_real_big_endian(value, 'f')

    def acn_encode_real_ieee745_64_big_endian(self, value):
        self.acn_encode_real_big_endian(value, 'd')

    def acn_encode_real_little_endian(self, value: float, format_type='f'):
        value_bytes = bytearray(struct.pack(format_type, value))

        if not self._requires_reverse():
            value_bytes = reversed(value_bytes)

        for byte in value_bytes:
            self.append_byte(byte)

    def acn_encode_real_ieee745_32_little_endian(self, value):
        self.acn_encode_real_little_endian(value, 'f')

    def acn_encode_real_ieee745_64_little_endian(self, value):
        self.acn_encode_real_little_endian(value, 'd')

    def acn_encode_string_ascii_fix_size(self, value, max_length=None):
        max_length = max_length or len(value)
        max_length = min(max_length, len(value))

        for i in range(max_length):
            char = value[i]
            self.append_byte(ord(char))

    def acn_encode_string_ascii_null_terminated(self, value, null_character, max_length):
        self.acn_encode_string_ascii_fix_size(value, max_length=max_length)
        self.append_byte(null_character)

    def acn_encode_string_ascii_external_field_determinant(self, value, max_length):
        self.acn_encode_string_ascii_fix_size(value, max_length=max_length)

    def acn_encode_string_ascii_internal_field_determinant(self, value, min_length, max_length):
        self.encode_constraint_number(min(len(value), max_length), min_length, max_length)
        self.acn_encode_string_ascii_fix_size(value, max_length=max_length)

    def acn_encode_string_char_index_fix_size(self, value, allowed_charset, max_length=None):
        max_length = max_length or len(value)
        max_length = min(max_length, len(value))

        for i in range(max_length):
            char = value[i]
            index = allowed_charset.index(char)
            self.encode_constraint_number(index, 0, len(allowed_charset) - 1)

    def acn_encode_string_char_index_external_field_determinant(self, value, allowed_charset, max_length):
        self.acn_encode_string_char_index_fix_size(value, allowed_charset, max_length=max_length)

    def acn_encode_string_char_index_internal_field_determinant(self, value, allowed_charset, min_length, max_length):
        self.encode_constraint_number(min(len(value), max_length), min_length, max_length)
        self.acn_encode_string_char_index_fix_size(value, allowed_charset, max_length=max_length)

    def acn_encode_length(self, value, length_size_in_bits):
        self.acn_encode_positive_integer_const_size(value, length_size_in_bits)

    def encode_milbus(self, value):
        return 32 if value == 0 else value

    # decoding

    def acn_decode_positive_integer_const_size(self, encoded_size_in_bits):
        return self.decode_non_negative_integer(encoded_size_in_bits)

    def acn_decode_positive_integer_const_size_byte(self, n_bytes, byteorder):
        if byteorder == 'little':
            return self._acn_decode_positive_integer_const_size_little_endian(n_bytes)
        elif byteorder == 'big':
            return self._acn_decode_positive_integer_const_size_big_endian(n_bytes)

    def _acn_decode_positive_integer_const_size_big_endian(self, n_bytes):
        value = 0
        for i in range(n_bytes):
            byte = self.read_byte()
            value <<= WORD_SIZE
            value |= byte

        return value

    def _acn_decode_positive_integer_const_size_little_endian(self, n_bytes):
        value = 0
        for i in range(n_bytes):
            byte = self.read_byte()
            byte <<= (i * WORD_SIZE)
            value |= byte

        return value

    def acn_decode_positive_integer_const_size_8(self):
        return self.read_byte()

    def acn_decode_positive_integer_const_size_16(self, byteorder):
        return self.acn_decode_positive_integer_const_size_byte(2, byteorder)

    def acn_decode_positive_integer_const_size_32(self, byteorder):
        return self.acn_decode_positive_integer_const_size_byte(4, byteorder)

    def acn_decode_positive_integer_const_size_64(self, byteorder):
        return self.acn_decode_positive_integer_const_size_byte(8, byteorder)

    def acn_decode_positive_integer_var_size_length_embedded(self):
        n_bytes = self.read_byte()
        value = 0

        for i in range(n_bytes):
            byte = self.read_byte()
            value <<= WORD_SIZE
            value |= byte

        return value

    def acn_decode_integer_twos_complement_const_size(self, encoded_size_in_bits):
        value = 0
        n_bytes = encoded_size_in_bits // WORD_SIZE
        rest_bits = encoded_size_in_bits % WORD_SIZE

        for i in range(n_bytes):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                value = -1

            value <<= WORD_SIZE
            value |= byte

        if rest_bits:
            byte = self.read_partial_byte(rest_bits)
            if n_bytes == 0 and byte > 127:
                value = -1

            value <<= rest_bits
            value |= byte >> (WORD_SIZE - rest_bits)

        return value

    def acn_decode_integer_twos_complement_const_size_8(self, ):
        return uint_to_int(self.acn_decode_positive_integer_const_size_8(), 1)

    def acn_decode_integer_twos_complement_const_size_16(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_16(byteorder), 2)

    def acn_decode_integer_twos_complement_const_size_32(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_32(byteorder), 4)

    def acn_decode_integer_twos_complement_const_size_64(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_64(byteorder), 8)

    def acn_decode_integer_twos_complement_var_size_length_embedded(self):
        n_bytes = self.read_byte()
        value = 0

        for i in range(n_bytes):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                value = -1

            value <<= WORD_SIZE
            value |= byte

        return value

    def acn_decode_integer_bcd_const_size(self, encoded_size_in_nibbles):
        result = 0
        for i in range(encoded_size_in_nibbles):
            digit = self.read_partial_byte(4) >> 4
            result *= 10
            result += digit

        return result

    def acn_decode_integer_bcd_var_size_length_embedded(self):
        n_nibbles = self.read_byte()
        return self.acn_decode_integer_bcd_const_size(n_nibbles)

    def acn_decode_integer_bcd_var_size_null_terminated(self):
        result = 0
        digit = self.read_partial_byte(4) >> 4

        while digit <= 9:
            result *= 10
            result += digit
            digit = self.read_partial_byte(4) >> 4

        return result

    def acn_decode_unsigned_integer_ascii_const_size(self, encoded_size_in_bytes):
        result = 0

        for i in range(encoded_size_in_bytes):
            digit = self.read_byte()
            assert ord('0') <= digit <= ord('9')
            result *= 10
            result += int(chr(digit))

        return result

    def acn_decode_signed_integer_ascii_const_size(self, encoded_size_in_bytes):
        sign = self.read_byte()
        assert sign in [ord('+'), ord('-')]
        sign = 1 if sign == ord('+') else -1
        result = self.acn_decode_unsigned_integer_ascii_const_size(encoded_size_in_bytes - 1)

        return sign * result

    def acn_decode_unsigned_integer_ascii_var_size_length_embedded(self):
        n_chars = self.read_byte()
        return self.acn_decode_unsigned_integer_ascii_const_size(n_chars)

    def acn_decode_signed_integer_ascii_var_size_length_embedded(self):
        n_chars = self.read_byte()
        return self.acn_decode_signed_integer_ascii_const_size(n_chars)

    def acn_decode_unsigned_integer_ascii_var_size_null_terminated(self):
        result = 0
        digit = self.read_byte()

        while digit:
            result *= 10
            result += int(chr(digit))
            digit = self.read_byte()

        return result

    def acn_decode_signed_integer_ascii_var_size_null_terminated(self):
        sign = self.read_byte()
        assert sign in [ord('+'), ord('-')]
        sign = 1 if sign == ord('+') else -1
        result = self.acn_decode_unsigned_integer_ascii_var_size_null_terminated()

        return sign * result

    def acn_decode_real_big_endian(self, format_type='f'):
        value_bytes = bytearray()

        for _ in bytearray(struct.pack(format_type, 0.0)):
            value_bytes.append(self.read_byte())

        if self._requires_reverse():
            value_bytes = bytes(reversed(value_bytes))

        return struct.unpack(format_type, value_bytes)[0]

    def acn_decode_real_ieee745_32_big_endian(self):
        return self.acn_decode_real_big_endian('f')

    def acn_decode_real_ieee745_64_big_endian(self):
        return self.acn_decode_real_big_endian('d')

    def acn_decode_real_little_endian(self, format_type='f'):
        value_bytes = bytearray()

        for _ in bytearray(struct.pack(format_type, 0.0)):
            value_bytes.append(self.read_byte())

        if not self._requires_reverse():
            value_bytes = bytes(reversed(value_bytes))

        return struct.unpack(format_type, value_bytes)[0]

    def acn_decode_real_ieee745_32_little_endian(self):
        return self.acn_decode_real_little_endian('f')

    def acn_decode_real_ieee745_64_little_endian(self):
        return self.acn_decode_real_little_endian('d')

    def acn_decode_string_ascii_fix_size(self, length):
        result = ''
        for i in range(length):
            char = self.read_byte()
            result += chr(char)

        return result

    def acn_decode_string_ascii_null_terminated(self, null_character, max_length):
        result = ''
        char = None
        for i in range(max_length + 1):
            char = self.read_byte()
            if char == null_character:
                break
            result += chr(char)

        if char != null_character:
            raise ValueError('No null terminated decoded!')

        return result

    def acn_decode_string_ascii_external_field_determinant(self, length, ext_field):
        return self.acn_decode_string_ascii_fix_size(min(length, ext_field))

    def acn_decode_string_ascii_internal_field_determinant(self, min_length, max_length):
        length = self.decode_constraint_number(min_length, max_length)
        return self.acn_decode_string_ascii_fix_size(length)

    def acn_decode_string_char_index_fix_size(self, length, allowed_charset):
        result = ''
        for i in range(length):
            index = self.decode_constraint_number(0, len(allowed_charset) - 1)
            result += allowed_charset[index]

        return result

    def acn_decode_string_char_index_external_field_determinant(self, length, allowed_charset, ext_field):
        return self.acn_decode_string_char_index_fix_size(min(length, ext_field), allowed_charset)

    def acn_decode_string_char_index_internal_field_determinant(self, allowed_charset, min_length, max_length):
        length = self.decode_constraint_number(min_length, max_length)
        return self.acn_decode_string_char_index_fix_size(length, allowed_charset)

    def acn_decode_length(self, length_size_in_bits):
        return self.acn_decode_positive_integer_const_size(length_size_in_bits)

    def decode_milbus(self, value):
        return 32 if value == 0 else value


#############################
#           Types           #
#############################


class ASN1Type:
    __constraints__ = ''

    def get(self):
        return self

    def set(self, value):
        if isinstance(value, ASN1Type):
            value = value.get()

        self.assert_correct_value(value)
        self._set_value(value)

    def assert_correct_value(self, value):
        if not self._is_correct_value(value):
            if isinstance(self, ASN1SimpleType):
                expected_type = self.__simple__

                if isinstance(self, Enumerated):
                    expected_type = ', '.join(['{}({})'.format(e.name, e.value) for e in self.Value][1:])

            elif isinstance(self, ASN1ArrayOfType):
                value = '{} elements'.format(len(value))
                expected_type = 'list of {}'.format(self.ElementType)

            else:
                expected_type = ASN1ComposedType

            raise ConstraintException(type(self).__name__, value, self.__constraints__, expected_type)

    def check_constraints(self, value):
        return True

    def _is_correct_value(self, value):
        return self._check_type(value) and self.check_constraints(value)

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

    def vars(self):
        return self.get()

    # Encoding and decoding functions

    def encode(self, bit_stream: BitStream, encoding=None, *args):
        self.assert_correct_value(self.get())

        if encoding == 'acn':
            self.acn_encode(bit_stream, *args)
        else:
            self.uper_encode(bit_stream)

        return self

    def acn_encode(self, bit_stream: BitStream, *args):
        raise NotImplementedEncoding('acn')

    def uper_encode(self, bit_stream: BitStream):
        raise NotImplementedEncoding('acn')

    def decode(self, bit_stream: BitStream, encoding=None, *args):
        if encoding == 'acn':
            self.acn_decode(bit_stream, *args)
        else:
            self.uper_decode(bit_stream)

        return self

    def acn_decode(self, bit_stream: BitStream, *args):
        raise NotImplementedEncoding('uper')

    def uper_decode(self, bit_stream: BitStream):
        raise NotImplementedEncoding('uper')


class ASN1SimpleType(ASN1Type):
    __simple__ = object

    def __init__(self, source=None):
        self.set(source or self.init_value())

    def init_value(self):
        return self.__simple__()

    def get(self):
        return self._value

    def _check_type(self, value):
        return isinstance(value, self.__simple__)

    def _set_value(self, value):
        self._value = value


class ASN1ComposedType(ASN1Type):
    __attributes__ = dict()
    __initialized__ = False

    def _check_type(self, value):
        return (
            (isinstance(value, ASN1ComposedType) and (isinstance(value, type(self)) or isinstance(self, type(value))))
            or isinstance(value, dict)
        )

    def _set_value(self, value):
        if isinstance(value, dict):
            self._init_from_dict(value)

        else:
            for attr in value.__attributes__:
                if value.__attributes__[attr]:
                    setattr(self, attr, object.__getattribute__(value, attr))

                self.__attributes__[attr] = value.__attributes__[attr]

    def _assert_attribute_present(self, item):
        if item in self.__attributes__ and not self.__attributes__[item]:
            raise AttributeError("Attribute {} not present!")

    def get_attribute_exists(self, key):
        return self.__attributes__[key]

    def set_attribute_exists(self, key, exists: bool):
        self.__attributes__[key] = exists

    def _init_from_dict(self, value):
        pass

    def __getattr__(self, item):
        raise AttributeError("Attribute {} not exists!".format(item))

    def __setattr__(self, key, value):
        if not self.__initialized__:
            object.__setattr__(self, key, value)

        elif key in self.__attributes__:
            object.__setattr__(self, key, value)
            self.set_attribute_exists(key, True)

        else:
            raise AttributeError("Can't set {} attribute!".format(key))

    def __delattr__(self, item):
        if item in self.__attributes__:
            self.set_attribute_exists(item, False)
        else:
            raise AttributeError("Can't delete {} attribute!".format(item))

    def __eq__(self, other):
        if not self._check_type(other):
            return False

        else:
            for attr in other.__attributes__:
                if other.__attributes__[attr] != self.__attributes__[attr]:
                    return False
                elif other.__attributes__[attr] and getattr(other, attr) != getattr(self, attr):
                    return False

            return True

    def __repr__(self):
        return str(vars(self))

    def vars(self):
        return {
            attr: getattr(self, '_' + attr).vars()
            for attr in self.__attributes__ if self.__attributes__[attr]
        }

    def __str__(self):
        return json.dumps(self.vars(), indent=2)


class ASN1StringWrappedType(ASN1SimpleType):
    @staticmethod
    def _wrap_string(wrapped, setter):
        class _StringWrapper(wrapped):
            __setter__ = setter

            def __init__(self, *args, **kwargs):
                if wrapped != str:
                    super().__init__(*args, **kwargs)
                self._wrap_methods()

            def _mutable_proxy(self, method):
                def proxy(*args, **kwargs):
                    method(*args, **kwargs)
                    self.__setter__(self)

                return proxy

            def _wrap_methods(self):
                mutable_methods = [
                    'append', 'clear', 'extend', 'insert', 'lstrip', 'pop', 'remove', 'rstrip', 'strip', '__setitem__'
                ]

                for method_name in mutable_methods:
                    if hasattr(self, method_name):
                        method = getattr(self, method_name)
                        setattr(self, method_name, self._mutable_proxy(method))

        return _StringWrapper

    def _set_value(self, value):
        self._value = self._wrap_string(self.__simple__, self.set)(value)

    def vars(self):
        return str(self._value)


T = typing.TypeVar('T')


class ASN1ArrayOfType(ASN1Type, typing.Generic[T]):
    ElementType = ASN1SimpleType

    def __init__(self, source=None):
        if source and isinstance(source, list):
            self._list = source
        elif source:
            self._list = self._get_new_list(source)
        else:
            self._list = self.init_value()

        self.set(self._list)

    def init_value(self):
        """:returns size of Array"""

        return 0

    def _get_new_list(self, size):
        element_list = list()

        for i in range(size):
            element_list.append(self.ElementType())

        return element_list

    def get(self):
        return self

    def _check_type(self, value):
        return isinstance(value, list) or isinstance(value, ASN1ArrayOfType)

    def _set_value(self, value):
        self._list = list()
        for i, elem in enumerate(value):
            if isinstance(elem, dict) and issubclass(self.ElementType, ASN1ComposedType):
                elem = self.ElementType(elem)

            tmp = self.ElementType()
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

    def __getitem__(self, item) -> T:
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

    def __iter__(self) -> typing.Iterable[T]:
        self._n = 0

        return self

    def __next__(self) -> T:
        if self._n < len(self._list):
            element = self._list[self._n]
            self._n += 1

            return element.get()

        else:
            raise StopIteration

    def __eq__(self, other):
        if isinstance(other, ASN1ArrayOfType):
            other = other._list

        if not isinstance(other, list):
            return False

        else:
            for i, elem in enumerate(other):
                if elem != self._list[i]:
                    return False

            return True

    def vars(self):
        return [elem.vars() for elem in self._list]

    def __str__(self):
        return json.dumps(self.vars(), indent=2)


class Enumerated(ASN1SimpleType):
    class Value(Enum):
        # NONE = None

        def __eq__(self, other):
            if isinstance(other, ASN1Type):
                other = other.get()
            if isinstance(other, Enum):
                other = other.value

            return self.value == other

    __simple__ = Value

    if typing.TYPE_CHECKING:
        def get(self) -> Enum: ...

    def init_value(self):
        enum_values = self._get_values_except_none()
        if enum_values:
            return self.Value(enum_values[0])
        return self.Value.NONE

    def _get_values_except_none(self):
        return [e.value for e in self.Value][1:]

    def _check_type(self, value):
        return super()._check_type(value) or value in [e.value for e in self.Value]

    def _set_value(self, value):
        if not isinstance(value, self.Value):
            value = self.Value(value)

        self._value = value

    def vars(self):
        return self._value.value


class Null(ASN1SimpleType):
    def __init__(self, source=None):
        super().__init__(source)
        self._value = None

    def init_value(self):
        return None

    def set(self, value):
        if value is not None:
            raise ConstraintException(type(self).__name__, value, "Null can't be set", None)


class Integer(ASN1SimpleType):
    __simple__ = int

    if typing.TYPE_CHECKING:
        def get(self) -> int: ...


class PosInteger(ASN1SimpleType):
    __simple__ = int

    if typing.TYPE_CHECKING:
        def get(self) -> int: ...

    def _check_type(self, value):
        return super()._check_type(value) and value >= 0


class Real(ASN1SimpleType):
    __simple__ = float

    if typing.TYPE_CHECKING:
        def get(self) -> float: ...

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)


class Boolean(ASN1SimpleType):
    __simple__ = bool

    if typing.TYPE_CHECKING:
        def get(self) -> bool: ...

    def _check_type(self, value):
        return isinstance(bool(value), bool)

    def _set_value(self, value):
        self._value = bool(value)


class BitString(ASN1StringWrappedType):
    __simple__ = bitarray

    if typing.TYPE_CHECKING:
        def get(self) -> bitarray: ...

    def set(self, value):
        if isinstance(value, bytes) or isinstance(value, bytearray):
            value = bitarray(value)

        super().set(value)

    def _check_type(self, value):
        return hasattr(value, '__iter__') and all([is_bit(c) for c in value])


class OctetString(ASN1StringWrappedType):
    __simple__ = bytearray

    if typing.TYPE_CHECKING:
        def get(self) -> bytearray: ...

    def _check_type(self, value):
        return super()._check_type(value) or isinstance(value, bytes)


class IA5String(ASN1StringWrappedType):
    __simple__ = str

    if typing.TYPE_CHECKING:
        def get(self) -> str: ...


class NumericString(ASN1StringWrappedType):
    __simple__ = str

    if typing.TYPE_CHECKING:
        def get(self) -> str: ...

    def _check_type(self, value):
        return super()._check_type(value) and str(value).replace(' ', '').isdigit() or not str(value).replace(' ', '')


class Sequence(ASN1ComposedType):
    __optionals__ = list()

    def _init_from_dict(self, source):
        for attribute in self.__attributes__:
            try:
                value = source[attribute]
                setattr(self, attribute, value)
            except KeyError:
                delattr(self, attribute)

    def set_attribute_exists(self, key, exists: bool):
        if not exists and key not in self.__optionals__:
            raise AttributeError("Attribute {} of {} object can't be Optional!".format(key, type(self).__name__))

        self.__attributes__[key] = exists


class Set(Sequence):
    pass


class Choice(ASN1ComposedType):
    def _init_from_dict(self, source):
        setattr(self, source['name'], source['value'])

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        self.set_attribute_exists(key, True)

    def set_attribute_exists(self, key, exists: bool):
        if exists:
            for choice in self.__attributes__:
                self.__attributes__[choice] = False

        self.__attributes__[key] = exists


class SequenceOf(ASN1ArrayOfType, typing.Generic[T]):
    pass


class SetOf(ASN1ArrayOfType, typing.Generic[T]):
    pass
