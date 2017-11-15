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

    return get_byte_length_from_bit_length(bit_length) or 1


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

    def _require_reverse(self):
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

    def read_partial_byte(self, n_bits):
        byte = 0
        for i in range(n_bits):
            bit = self.read_bit()
            byte |= bit << (WORD_SIZE - i - 1)

        return byte

    def read_bit_pattern(self, pattern, n_bits):
        value = True
        n_bytes = n_bits / WORD_SIZE
        rest_bits = n_bits % WORD_SIZE

        for i in range(n_bytes):
            byte = self.read_byte()
            if byte != pattern[i]:
                value = False

        if rest_bits:
            byte = self.read_partial_byte(rest_bits)
            if byte != pattern[n_bytes] >> (WORD_SIZE - rest_bits):
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
            value /= 10
            result += 1

        return result

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
        if value >= 0:
            self.append_bits_zero(encoded_size_in_bits - value.bit_length())
            self.encode_non_negative_integer(value)

        else:
            self.append_bits_one(encoded_size_in_bits - (-value).bit_length())
            self.encode_non_negative_integer(-value - 1, True)

    def acn_encode_integer_twos_complement_const_size_8(self, value):
        self.acn_encode_positive_integer_const_size_8(value)

    def acn_encode_integer_twos_complement_const_size_16(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_16(value, byteorder)

    def acn_encode_integer_twos_complement_const_size_32(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_32(value, byteorder)

    def acn_encode_integer_twos_complement_const_size_64(self, value, byteorder):
        self.acn_encode_positive_integer_const_size_64(value, byteorder)

    def acn_encode_integer_twos_complement_var_size(self, value):
        self.acn_encode_positive_integer_var_size_length_embedded(value)

    def acn_encode_integer_bcd_const_size(self, value, encoded_size_in_nibbles):
        assert encoded_size_in_nibbles <= 100

        digits = list()
        while value > 0:
            digits.append(value % 10)
            value /= 10

        assert len(digits) <= encoded_size_in_nibbles

        for digit in reversed(digits):
            self.append_partial_byte(digit & 0xF, 4)

    def acn_encode_integer_bcd_var_size_length_embedded(self, value):
        n_nibbles = self.acn_get_integer_size_bcd(value)
        self.append_byte(n_nibbles & 0xFFFFFFFF)
        self.acn_encode_integer_bcd_const_size(value, n_nibbles)

    def acn_encode_integer_bcd_var_size_null_terminated(self, value):
        n_nibbles = self.acn_get_integer_size_bcd(value)
        self.acn_encode_integer_bcd_const_size(value, n_nibbles)
        self.append_partial_byte(0xF, 4)

    def acn_encode_unsigned_integer_ascii_const_size(self, value, encoded_size_in_bytes):
        assert encoded_size_in_bytes <= 100

        digits = list()
        while value > 0:
            digits.append(value % 10)
            value /= 10

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
        n_chars = self.acn_get_integer_size_bcd(value)
        self.append_byte(n_chars)
        self.acn_encode_signed_integer_ascii_const_size(value, n_chars)

    def acn_encode_unsigned_integer_ascii_var_size_null_terminated(self, value):
        n_chars = self.acn_get_integer_size_bcd(value)
        self.acn_encode_unsigned_integer_ascii_const_size(value, n_chars)
        self.append_byte(0)

    def acn_encode_signed_integer_ascii_var_size_null_terminated(self, value):
        n_chars = self.acn_get_integer_size_bcd(value)
        self.acn_encode_signed_integer_ascii_const_size(value, n_chars)
        self.append_byte(0)

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
        n_bytes = encoded_size_in_bits / WORD_SIZE
        rest_bits = encoded_size_in_bits % WORD_SIZE

        for i in range(n_bytes):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                value = -1

            value <<= WORD_SIZE
            value |= byte

        if rest_bits:
            value <<= rest_bits
            value |= self.read_partial_byte(rest_bits) >> (WORD_SIZE - rest_bits)

        return value

    def acn_decode_integer_twos_complement_const_size_8(self, ):
        return uint_to_int(self.acn_decode_positive_integer_const_size_8(), 1)

    def acn_decode_integer_twos_complement_const_size_16(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_16(byteorder), 2)

    def acn_decode_integer_twos_complement_const_size_32(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_32(byteorder), 4)

    def acn_decode_integer_twos_complement_const_size_64(self, byteorder):
        return uint_to_int(self.acn_decode_positive_integer_const_size_64(byteorder), 8)

    def acn_decode_integer_var_size_length_embedded(self):
        n_bytes = self.read_byte()
        value = 0
        negate = False

        for i in range(n_bytes):
            byte = self.read_byte()
            if i == 0 and byte > 127:
                value = -1
                negate = True

            value <<= WORD_SIZE
            value |= byte

        if negate:
            value = ~value

        return value

    def acn_decode_integer_bcd_const_size(self, encoded_size_in_nibbles):
        result = 0
        while encoded_size_in_nibbles > 0:
            digit = self.read_partial_byte(4)
            result *= 10
            result += digit
            encoded_size_in_nibbles -= 1

        return result

    def acn_decode_integer_bcd_var_size_length_embedded(self):
        n_nibbles = self.read_byte()
        return self.acn_decode_integer_bcd_const_size(n_nibbles)

    def acn_decode_integer_bcd_var_size_null_terminated(self):
        result = 0
        digit = self.read_partial_byte(4)

        while digit <= 9:
            result *= 10
            result += digit
            digit = self.read_partial_byte(4)

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

        if self._is_correct_value(value):
            self._set_value(value)

        else:
            if isinstance(self, ASN1SimpleType):
                expected_type = self.__simple__

                if isinstance(self, Enumerated):
                    expected_type = ', '.join(['{}({})'.format(e.name, e.value) for e in self.Value][1:])

            elif isinstance(self, ASN1ArrayOfType):
                value = '{} elements'.format(len(value))
                expected_type = 'list of {}'.format(self.__element__)

            else:
                expected_type = ASN1ComposedType

            raise ConstraintException(type(self).__name__, value, self.constraints, expected_type)

    @classmethod
    def check_constraints(cls, value):
        return True

    @classmethod
    def _is_correct_value(cls, value):
        if isinstance(value, ASN1Type):
            value = value.get()

        return cls._check_type(value) and cls.check_constraints(value)

    @classmethod
    def _check_type(cls, value):
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

    @classmethod
    def encode(cls, bit_stream: BitStream, value, encoding=None):
        if isinstance(value, cls):
            value = value.get()

        if not cls._is_correct_value(value):
            raise Exception("{} can't encode {}".format(cls.__name__, value))

        if encoding == 'acn':
            cls._acn_encode(bit_stream, value)
        else:
            cls._uper_encode(bit_stream, value)

    @classmethod
    def _acn_encode(cls, bit_stream: BitStream, value):
        pass

    @classmethod
    def _uper_encode(cls, bit_stream: BitStream, value):
        pass

    @classmethod
    def decode(cls, bit_stream: BitStream, encoding=None) -> typing.Any:
        if encoding == 'acn':
            value = cls._acn_decode(bit_stream)
        else:
            value = cls._uper_decode(bit_stream)

        if not cls._is_correct_value(value):
            raise Exception("{} can't decode {}".format(cls.__name__, value))

        return value

    @classmethod
    def _acn_decode(cls, bit_stream: BitStream):
        return 0

    @classmethod
    def _uper_decode(cls, bit_stream: BitStream):
        return 0


T = typing.TypeVar('T')


class ASN1SimpleType(ASN1Type, typing.Generic[T]):
    __simple__ = object

    def __init__(self, source=None):
        self.set(source or self.init_value())

    @classmethod
    def init_value(cls):
        return cls.__simple__()

    def get(self) -> T:
        return self._value

    @classmethod
    def _check_type(cls, value):
        return isinstance(value, cls.__simple__)

    def _set_value(self, value):
        self._value = value


class ASN1ComposedType(ASN1Type):
    attributes = dict()
    initialized = False

    @classmethod
    def _check_type(cls, value):
        return isinstance(value, ASN1ComposedType) and (isinstance(value, cls) or issubclass(cls, type(value)))

    def _set_value(self, value):
        for attr in value.attributes:
            if value.attributes[attr]:
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


class ASN1StringWrappedType(ASN1SimpleType, typing.Generic[T]):
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


class ASN1ArrayOfType(ASN1Type, typing.Generic[T]):
    __typing__ = 'ASN1ArrayOfType'
    __element__ = ASN1SimpleType

    def __init__(self, source=None):
        if source and isinstance(source, list):
            self._list = source
        else:
            self._list = self._get_new_list(source or self.init_value())

        self.set(self._list)

    @classmethod
    def init_value(cls):
        """:returns size of Array"""

        return 0

    def _get_new_list(self, size):
        element_list = list()

        for i in range(size):
            element_list.append(self.__element__())

        return element_list

    def get(self) -> typing.List[T]:
        return self._list

    @classmethod
    def _check_type(cls, value):
        return isinstance(value, list)

    def _set_value(self, value):
        self._list = list()
        for i, elem in enumerate(value):
            if isinstance(elem, dict) and issubclass(self.__element__, ASN1ComposedType):
                elem = self.__element__(elem)

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
        if isinstance(other, self.__class__):
            other = other.get()

        if not isinstance(other, list):
            return False

        else:
            for i, elem in enumerate(other):
                if elem != self._list[i]:
                    return False

            return True

    def __str__(self):
        return str([str(elem) for elem in self._list])


class Enumerated(ASN1SimpleType[Enum]):
    class Value(Enum):
        # NONE = None

        def __eq__(self, other):
            if isinstance(other, ASN1Type):
                other = other.get()
            if isinstance(other, Enum):
                other = other.value

            return self.value == other

    __simple__ = Value
    __typing__ = Value

    @classmethod
    def init_value(cls):
        enum_values = cls._get_values_except_none()
        if enum_values:
            return cls.Value(enum_values[0])
        return cls.Value.NONE

    @classmethod
    def _check_type(cls, value):
        return super()._check_type(value) or value in [e.value for e in cls.Value]

    def _set_value(self, value):
        if not isinstance(value, self.Value):
            value = self.Value(value)

        self._value = value

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value):
        if isinstance(value, cls.Value):
            value = value.value

        enum_values = cls._get_values_except_none()
        value_index = enum_values.index(value)

        bit_stream.encode_constraint_number(value_index, 0, len(enum_values) - 1)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream):
        enum_values = cls._get_values_except_none()
        value_index = bit_stream.decode_constraint_number(0, len(enum_values) - 1)

        return enum_values[value_index]

    @classmethod
    def _get_values_except_none(cls):
        return [e.value for e in cls.Value][1:]


class Null(ASN1SimpleType[None]):
    def __init__(self):
        super().__init__(None)
        self._value = None

    @classmethod
    def init_value(cls):
        return None

    def set(self, value):
        if value is not None:
            raise ConstraintException(type(self).__name__, value, "Null can't be set", None)


class Integer(ASN1SimpleType[int]):
    __simple__ = int
    __typing__ = int

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_val=None, max_val=None):
        if min_val and max_val:
            if min_val != max_val:
                bit_stream.encode_constraint_number(value, min_val, max_val)

        else:
            bit_stream.encode_number(value)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_val=None, max_val=None):
        if min_val and max_val:
            if min_val != max_val:
                return bit_stream.decode_constraint_number(min_val, max_val)

            else:
                return cls.init_value()

        else:
            return bit_stream.decode_number()


class Real(ASN1SimpleType[float]):
    __simple__ = float
    __typing__ = float

    @classmethod
    def _check_type(cls, value):
        return super()._check_type(value) or isinstance(value, int)

    def _set_value(self, value):
        self._value = float(value)

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_val=None, max_val=None):
        bit_stream.encode_real(value)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_val=None, max_val=None):
        return bit_stream.decode_real()


class Boolean(ASN1SimpleType[bool]):
    __simple__ = bool
    __typing__ = bool

    @classmethod
    def _check_type(cls, value):
        return isinstance(bool(value), bool)

    def _set_value(self, value):
        self._value = bool(value)

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value):
        bit_stream.append_bit(int(value))

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream):
        return bool(bit_stream.read_bit())


class BitString(ASN1StringWrappedType[bitarray]):
    __simple__ = bitarray
    __typing__ = bitarray

    def set(self, value):
        if isinstance(value, bytes) or isinstance(value, bytearray):
            value = bitarray(value)

        super().set(value)

    @classmethod
    def _check_type(cls, value):
        return hasattr(value, '__iter__') and all([is_bit(c) for c in value])

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_size, max_size):
        if min_size != max_size:
            bit_stream.encode_constraint_number(len(value), min_size, max_size)

        bit_stream.append_bits(value.bytes(), len(value))

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_size, max_size):
        if min_size != max_size:
            min_size = bit_stream.decode_constraint_number(min_size, max_size)

        return bit_stream.read_bits(min_size)


class OctetString(ASN1StringWrappedType[bytearray]):
    __simple__ = bytearray
    __typing__ = bytearray

    @classmethod
    def _check_type(cls, value):
        return super()._check_type(value) or isinstance(value, bytes)

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_size, max_size):
        if min_size != max_size:
            bit_stream.encode_constraint_number(len(value), min_size, max_size)

        for byte in value:
            bit_stream.append_byte(byte)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_size, max_size):
        if min_size != max_size:
            min_size = bit_stream.decode_constraint_number(min_size, max_size)

        result = bytearray()
        for i in range(min_size):
            byte = bit_stream.read_byte()
            result.append(byte)

        return result


class IA5String(ASN1StringWrappedType[str]):
    __simple__ = str
    __typing__ = str

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_size, max_size):
        if min_size != max_size:
            bit_stream.encode_constraint_number(len(value), min_size, max_size)

        for char in value:
            bit_stream.encode_constraint_number(ord(char), 0, 127)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_size, max_size):
        if min_size != max_size:
            min_size = bit_stream.decode_constraint_number(min_size, max_size)

        result = ''
        for i in range(min_size):
            char = bit_stream.decode_constraint_number(0, 127)
            result += chr(char)

        return result


class NumericString(ASN1StringWrappedType[str]):
    __simple__ = str
    __typing__ = str

    @classmethod
    def _check_type(cls, value):
        return super()._check_type(value) and str(value).replace(' ', '').isdigit()

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_size, max_size):
        if min_size != max_size:
            bit_stream.encode_constraint_number(len(value), min_size, max_size)

        for num in value:
            num = int(num) + 1 if num != ' ' else 0
            bit_stream.encode_constraint_number(num, 0, 10)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_size, max_size):
        if min_size != max_size:
            min_size = bit_stream.decode_constraint_number(min_size, max_size)

        result = ''
        for i in range(min_size):
            num = bit_stream.decode_constraint_number(0, 10)
            num = str(num - 1) if num else ' '
            result += num

        return result


class Sequence(ASN1ComposedType):
    optionals = list()

    def _init_from_source(self, source):
        if not source:  # default initialization
            return

        for attribute in self.attributes:
            self.attributes[attribute] = False
            value = source.get(attribute, None)
            setattr(self, attribute, value)

    def _set_attribute_exists(self, key, exists: bool):
        if not exists and key not in self.optionals:
            raise AttributeError("Attribute {} of {} object can't be Optional!".format(key, type(self).__name__))

        self.attributes[key] = exists

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value):
        for opt in value.optionals:
            bit_stream.append_bit(int(value.attributes[opt]))

        for attr, exists in value.attributes.items():
            if exists:
                attribute = object.__getattribute__(value, attr)
                attribute.encode(bit_stream, attribute.get())

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream):
        result = cls()
        opt_mask = bit_stream.read_bits(len(result.optionals))

        for i, opt in enumerate(result.optionals):
            result.attributes[opt] = bool(opt_mask[i // WORD_SIZE] >> (7 - i) & 1)

        for attr in result.attributes:
            if result.attributes[attr]:
                attribute = object.__getattribute__(result, attr)
                setattr(result, attr, attribute.decode(bit_stream))

        return result


class Set(Sequence):
    pass


class Choice(ASN1ComposedType):
    def _init_choice(self, choice):
        if choice:
            attribute = object.__getattribute__(self, choice['name'])
            setattr(self, choice['name'], attribute.__class__(choice['value']))

        else:
            self._set_choice(list(self.attributes.keys())[0])

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        self._set_choice(key)

    def _set_choice(self, key):
        for choice in self.attributes:
            self.attributes[choice] = False

            if choice == key:
                self.attributes[choice] = True

    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value):
        choice_index = 0
        choice_attr = list(value.attributes.keys())[0]

        for attr, exists in value.attributes.items():
            if exists:
                break
            choice_index += 1
            choice_attr = attr

        bit_stream.encode_constraint_number(choice_index, 0, len(value.attributes) - 1)

        attribute = object.__getattribute__(value, choice_attr)
        attribute.encode(bit_stream, attribute.get())

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream):
        result = cls()
        choice_index = bit_stream.decode_constraint_number(0, len(result.attributes) - 1)
        choice_attr = list(result.attributes.keys())[choice_index]

        attribute = object.__getattribute__(result, choice_attr)
        setattr(result, choice_attr, attribute.decode(bit_stream))

        return result


class SequenceOf(ASN1ArrayOfType, typing.Generic[T]):
    @classmethod
    def _default_uper_encode(cls, bit_stream: BitStream, value, min_size, max_size):
        if min_size != max_size:
            bit_stream.encode_constraint_number(len(value), min_size, max_size)

        for elem in value:
            cls.__element__.encode(bit_stream, elem)

    @classmethod
    def _default_uper_decode(cls, bit_stream: BitStream, min_size, max_size):
        if min_size != max_size:
            min_size = bit_stream.decode_constraint_number(min_size, max_size)

        tmp = list()
        for i in range(min_size):
            x = cls.__element__.decode(bit_stream)
            tmp.append(x)

        result = cls(tmp)
        return result


class SetOf(SequenceOf, typing.Generic[T]):
    pass
