import unittest

from stockroom import store


class StoreTests(unittest.TestCase):
    def setUp(self):
        store.reset()

    def test_ids_increase(self):
        first = store.add_item("bolt", 10, 0.25)
        second = store.add_item("nut", 5, 0.10)
        self.assertEqual((first["id"], second["id"]), (1, 2))

    def test_an_added_item_can_be_read_back(self):
        store.add_item("bolt", 10, 0.25)
        self.assertEqual(store.get_item(1)["name"], "bolt")
