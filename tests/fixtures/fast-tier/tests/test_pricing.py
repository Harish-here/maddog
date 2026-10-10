import unittest

from stockroom.pricing import line_total


class PricingTests(unittest.TestCase):
    def test_whole_price(self):
        self.assertEqual(line_total(3, 2), 6)

    def test_zero_quantity(self):
        self.assertEqual(line_total(0, 9.99), 0)

    def test_fractional_price(self):
        self.assertEqual(line_total(4, 2.5), 10.0)
