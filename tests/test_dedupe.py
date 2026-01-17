import unittest

from core.merge.dedupe import ContactIndex
from core.models import Contact


class TestDedupe(unittest.TestCase):
    def test_dedupe_by_phone(self) -> None:
        index = ContactIndex()
        first = Contact(name="Maria", phone="5511912345678")
        second = Contact(name=".", phone="5511912345678")

        merged_first = index.add(first)
        merged_second = index.add(second)

        self.assertFalse(merged_first)
        self.assertTrue(merged_second)
        self.assertEqual(len(index), 1)
        self.assertEqual(index.duplicates_merged, 1)
        self.assertEqual(index.values()[0].name, "Maria")


if __name__ == "__main__":
    unittest.main()
