import unittest

from stockroom.labels import label_for


class LabelTests(unittest.TestCase):
    def test_label_shows_the_price(self):
        self.assertEqual(label_for({"name": "bolt", "price": 0.25}), "bolt  $0.25")

    def test_label_rounds_to_cents(self):
        self.assertEqual(label_for({"name": "nut", "price": 0.1}), "nut  $0.10")
