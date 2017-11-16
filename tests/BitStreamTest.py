from unittest import TestCase

import asn1
from asn1 import BitStream


class BitStreamTest(TestCase):
    def setUp(self):
        self.b = BitStream()

    def test_append_read_bit(self):
        self.b.append_bit(1)

        self.b2 = BitStream(self.b)
        self.assertEqual(1, self.b2.read_bit())

    def test_append_read_byte(self):
        self.b.append_byte(123)

        self.b2 = BitStream(self.b)
        self.assertEqual(123, self.b2.read_byte())

    def test_append_read_byte_negate(self):
        self.b.append_byte(~(-200), True)

        self.b2 = BitStream(self.b)
        self.assertEqual(56, self.b2.read_byte())

    def test_append_read_partial_byte(self):
        self.b.append_partial_byte(0b10100101, 3)

        self.b2 = BitStream(self.b)
        self.assertEqual(0b10100000, self.b2.read_partial_byte(3))

    def test_append_read_partial_byte_negate(self):
        self.b.append_partial_byte(0b10100101, 3, True)

        self.b2 = BitStream(self.b)
        self.assertEqual(0b01000000, self.b2.read_partial_byte(3))

    def test_append_read_bits(self):
        self.b.append_bits(bytearray([0b10100101, 0b11001100]), 9)
        self.b2 = BitStream(self.b)
        self.assertEqual(bytearray([0b10100101, 0b10000000]), self.b2.read_bits(9))

    def test_read_bit_pattern(self):
        self.b.append_bits(bytearray([0b10100101, 0b11001100, 0b11101111]), 20)

        self.b2 = BitStream(self.b)
        self.assertTrue(self.b2.read_bit_pattern(bytearray([0b10100101, 0b11001100, 0b11101111]), 10))

    def test_encode_decode_non_negative_integer32_0(self):
        self.b.encode_non_negative_integer32(0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0, self.b2.decode_non_negative_integer32(0))

    def test_encode_decode_non_negative_integer32_little(self):
        self.b.encode_non_negative_integer32(33)

        self.b2 = BitStream(self.b)
        self.assertEqual(33, self.b2.decode_non_negative_integer32(6))

    def test_encode_decode_non_negative_integer32_medium(self):
        self.b.encode_non_negative_integer32(321)
        self.b2 = BitStream(self.b)
        self.assertEqual(321, self.b2.decode_non_negative_integer32(int(321).bit_length()))

    def test_encode_decode_non_negative_integer32_big(self):
        self.b.encode_non_negative_integer32(3217)

        self.b2 = BitStream(self.b)
        self.assertEqual(3217, self.b2.decode_non_negative_integer32(int(3217).bit_length()))

    def test_encode_decode_non_negative_integer32_plus_max(self):
        self.b.encode_non_negative_integer32(asn1.INT_MAX)

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INT_MAX, self.b2.decode_non_negative_integer32(int(asn1.INT_MAX).bit_length()))

    def test_encode_decode_non_negative_integer_plus_max(self):
        self.b.encode_non_negative_integer(asn1.INT_MAX)

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INT_MAX, self.b2.decode_non_negative_integer(int(asn1.INT_MAX).bit_length()))

    def test_encode_decode_non_negative_integer_more(self):
        self.b.encode_non_negative_integer(0x1ffffffff)

        self.b2 = BitStream(self.b)
        self.assertEqual(0x1ffffffff, self.b2.decode_non_negative_integer32(int(0x1ffffffff).bit_length()))

    def test_encode_decode_constraint_number_0(self):
        self.b.encode_constraint_number(0, 0, 0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0, self.b2.decode_constraint_number(0, 0))

    def test_encode_decode_constraint_number_little(self):
        self.b.encode_constraint_number(5, 1, 10)

        self.b2 = BitStream(self.b)
        self.assertEqual(5, self.b2.decode_constraint_number(1, 10))

    def test_encode_decode_constraint_number_medium(self):
        self.b.encode_constraint_number(1234, 12, 2342)

        self.b2 = BitStream(self.b)
        self.assertEqual(1234, self.b2.decode_constraint_number(12, 2342))

    def test_encode_decode_constraint_number_big(self):
        self.b.encode_constraint_number(123433, 1222, 234211)

        self.b2 = BitStream(self.b)
        self.assertEqual(123433, self.b2.decode_constraint_number(1222, 234211))

    def test_encode_decode_constraint_number_big_little_range(self):
        self.b.encode_constraint_number(234210, 234209, 234211)

        self.b2 = BitStream(self.b)
        self.assertEqual(234210, self.b2.decode_constraint_number(234209, 234211))
        self.assertEqual(2, self.b._current_bit)

    def test_encode_decode_semi_constraint_number_0(self):
        self.b.encode_semi_constraint_number(0, 0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0, self.b2.decode_semi_constraint_number(0))

    def test_encode_decode_semi_constraint_number_little(self):
        self.b.encode_semi_constraint_number(23, 2)

        self.b2 = BitStream(self.b)
        self.assertEqual(23, self.b2.decode_semi_constraint_number(2))

    def test_encode_decode_semi_constraint_number_medium(self):
        self.b.encode_semi_constraint_number(12345, 432)

        self.b2 = BitStream(self.b)
        self.assertEqual(12345, self.b2.decode_semi_constraint_number(432))

    def test_encode_decode_semi_constraint_number_big(self):
        self.b.encode_semi_constraint_number(234234234, 0)

        self.b2 = BitStream(self.b)
        self.assertEqual(234234234, self.b2.decode_semi_constraint_number(0))

    def test_encode_decode_semi_constraint_number_big_little_semi(self):
        self.b.encode_semi_constraint_number(234234234, 234234233)

        self.b2 = BitStream(self.b)
        self.assertEqual(234234234, self.b2.decode_semi_constraint_number(234234233))

    def test_encode_decode_number_0(self):
        self.b.encode_number(0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0, self.b2.decode_number())

    def test_encode_decode_number_1(self):
        self.b.encode_number(1)

        self.b2 = BitStream(self.b)
        self.assertEqual(1, self.b2.decode_number())

    def test_encode_decode_number_127(self):
        self.b.encode_number(127)

        self.b2 = BitStream(self.b)
        self.assertEqual(127, self.b2.decode_number())

    def test_encode_decode_number_255(self):
        self.b.encode_number(255)

        self.b2 = BitStream(self.b)
        self.assertEqual(255, self.b2.decode_number())

    def test_encode_decode_number_256(self):
        self.b.encode_number(256)

        self.b2 = BitStream(self.b)
        self.assertEqual(256, self.b2.decode_number())

    def test_encode_decode_number_12345(self):
        self.b.encode_number(12345)

        self.b2 = BitStream(self.b)
        self.assertEqual(12345, self.b2.decode_number())

    def test_encode_decode_number_max(self):
        self.b.encode_number(asn1.INT_MAX)

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INT_MAX, self.b2.decode_number())

    def test_encode_decode_number_minus_1(self):
        self.b.encode_number(-1)

        self.b2 = BitStream(self.b)
        self.assertEqual(-1, self.b2.decode_number())

    def test_encode_decode_number_minus_127(self):
        self.b.encode_number(-127)

        self.b2 = BitStream(self.b)
        self.assertEqual(-127, self.b2.decode_number())

    def test_encode_decode_number_minus_255(self):
        self.b.encode_number(-255)

        self.b2 = BitStream(self.b)
        self.assertEqual(-255, self.b2.decode_number())

    def test_encode_decode_number_minus_256(self):
        self.b.encode_number(-256)

        self.b2 = BitStream(self.b)
        self.assertEqual(-256, self.b2.decode_number())

    def test_encode_decode_number_minus_12345(self):
        self.b.encode_number(-12345)

        self.b2 = BitStream(self.b)
        self.assertEqual(-12345, self.b2.decode_number())

    def test_encode_decode_number_minus_max(self):
        self.b.encode_number(asn1.INT_MIN)

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INT_MIN, self.b2.decode_number())

    def test_encode_decode_real_0(self):
        self.b.encode_real(0.0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0.0, self.b2.decode_real())

    def test_encode_decode_real_1_234(self):
        self.b.encode_real(1.234)

        self.b2 = BitStream(self.b)
        self.assertEqual(1.234, self.b2.decode_real())

    def test_encode_decode_real_0_5(self):
        self.b.encode_real(0.5)

        self.b2 = BitStream(self.b)
        self.assertEqual(0.5, self.b2.decode_real())

    def test_encode_decode_real_16(self):
        self.b.encode_real(16)

        self.b2 = BitStream(self.b)
        self.assertEqual(16, self.b2.decode_real())

    def test_encode_decode_real_int_max(self):
        self.b.encode_real(asn1.INT_MAX)

        self.b2 = BitStream(self.b)
        self.assertAlmostEqual(float(asn1.INT_MAX), self.b2.decode_real(), delta=0.001)

    def test_encode_decode_real_minus_1_234(self):
        self.b.encode_real(-1.234)

        self.b2 = BitStream(self.b)
        self.assertEqual(-1.234, self.b2.decode_real())

    def test_encode_decode_real_minus_0_5(self):
        self.b.encode_real(-0.5)

        self.b2 = BitStream(self.b)
        self.assertEqual(-0.5, self.b2.decode_real())

    def test_encode_decode_real_minus_16(self):
        self.b.encode_real(-16)

        self.b2 = BitStream(self.b)
        self.assertEqual(-16, self.b2.decode_real())

    def test_encode_decode_real_int_min(self):
        self.b.encode_real(asn1.INT_MIN)

        self.b2 = BitStream(self.b)
        self.assertAlmostEqual(float(asn1.INT_MIN), self.b2.decode_real(), delta=0.001)

    def test_encode_decode_real_inf(self):
        self.b.encode_real(asn1.INFINITY)

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INFINITY, self.b2.decode_real())

    def test_encode_decode_real_minus_inf(self):
        self.b.encode_real(-asn1.INFINITY)

        self.b2 = BitStream(self.b)
        self.assertEqual(-asn1.INFINITY, self.b2.decode_real())

    # acn

    def test_integer_size_bcd(self):
        self.assertEqual(self.b.acn_get_integer_size_bcd(123456789), 9)

    def test_integer_size_ascii(self):
        self.assertEqual(self.b.acn_get_integer_size_ascii(-123456789), 10)

    def test_acn_encode_decode_positive_integer_const_size_0_0(self):
        self.b.acn_encode_positive_integer_const_size(0, 0)

        self.b2 = BitStream(self.b)
        self.assertEqual(0, self.b2.acn_decode_positive_integer_const_size(0))

    def test_acn_encode_decode_positive_integer_const_size_1_1(self):
        self.b.acn_encode_positive_integer_const_size(1, 1)

        self.b2 = BitStream(self.b)
        self.assertEqual(1, self.b2.acn_decode_positive_integer_const_size(1))

    def test_acn_encode_decode_positive_integer_const_size_1_10(self):
        self.b.acn_encode_positive_integer_const_size(1, 10)

        self.b2 = BitStream(self.b)
        self.assertEqual(1, self.b2.acn_decode_positive_integer_const_size(10))

    def test_acn_encode_decode_positive_integer_const_size_255_10(self):
        self.b.acn_encode_positive_integer_const_size(255, 10)

        self.b2 = BitStream(self.b)
        self.assertEqual(255, self.b2.acn_decode_positive_integer_const_size(10))

    def test_acn_encode_decode_positive_integer_const_size_max_10(self):
        self.b.acn_encode_positive_integer_const_size(asn1.INT_MAX, 10)

        self.b2 = BitStream(self.b)
        max_10_bits = asn1.INT_MAX >> asn1.INT_MAX.bit_length() - 10
        self.assertEqual(max_10_bits, self.b2.acn_decode_positive_integer_const_size(10))

    def test_acn_encode_decode_positive_integer_const_size_max_max(self):
        self.b.acn_encode_positive_integer_const_size(asn1.INT_MAX, asn1.INT_MAX.bit_length())

        self.b2 = BitStream(self.b)
        self.assertEqual(asn1.INT_MAX, self.b2.acn_decode_positive_integer_const_size(asn1.INT_MAX.bit_length()))