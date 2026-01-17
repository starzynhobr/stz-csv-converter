import unittest

from core.normalize.name import build_fallback_name, is_phone_like_name


class TestNameFallback(unittest.TestCase):
    def test_phone_like_detection(self) -> None:
        self.assertTrue(is_phone_like_name("5511912345678"))
        self.assertTrue(is_phone_like_name("(11) 91234-5678"))
        self.assertTrue(is_phone_like_name("."))
        self.assertFalse(is_phone_like_name("Mariano Ângelo"))
        self.assertFalse(is_phone_like_name("Honda"))

    def test_build_fallback_name(self) -> None:
        name = build_fallback_name("Cliente", 1, "5511912345678")
        self.assertEqual(name, "Cliente 0000001 (5678)")


if __name__ == "__main__":
    unittest.main()
