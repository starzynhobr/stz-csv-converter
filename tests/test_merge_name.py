import unittest

from core.merge.merge_rules import merge_name


class TestMergeName(unittest.TestCase):
    def test_keep_existing_good_name(self) -> None:
        self.assertEqual(merge_name("Maria Silva", "."), "Maria Silva")

    def test_use_incoming_if_existing_empty(self) -> None:
        self.assertEqual(merge_name(".", "Joao"), "Joao")


if __name__ == "__main__":
    unittest.main()
