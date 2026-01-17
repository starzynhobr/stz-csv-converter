import unittest

from core.normalize.phone import normalize_phone


class TestPhoneNormalize(unittest.TestCase):
    def test_normalize_with_default_ddi(self) -> None:
        self.assertEqual(
            normalize_phone("(11) 91234-5678", "55", True),
            "5511912345678",
        )

    def test_normalize_with_existing_ddi(self) -> None:
        self.assertEqual(
            normalize_phone("+55 11 91234-5678", "55", True),
            "5511912345678",
        )

    def test_normalize_with_override_ddi(self) -> None:
        self.assertEqual(
            normalize_phone("11912345678", "55", True, "1"),
            "111912345678",
        )


if __name__ == "__main__":
    unittest.main()
