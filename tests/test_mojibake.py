import unittest

from core.normalize import text
from core.normalize.text import analyze_mojibake


class TestMojibakeDetection(unittest.TestCase):
    def test_valid_pt_br_names_are_not_suspect(self) -> None:
        samples = [
            "Mariano Ângelo",
            "Mãe",
            "Cachorrão",
            "Ângela",
            "João 😊",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                result = analyze_mojibake(sample)
                self.assertFalse(result.suspect)

    def test_mojibake_is_suspect(self) -> None:
        result = analyze_mojibake("MÃ¡rcio")
        self.assertTrue(result.suspect)
        if text.ftfy is not None:
            self.assertEqual(result.suggested_fix, "Márcio")

    def test_replacement_char_is_suspect(self) -> None:
        result = analyze_mojibake("Nome \ufffd")
        self.assertTrue(result.suspect)


if __name__ == "__main__":
    unittest.main()
