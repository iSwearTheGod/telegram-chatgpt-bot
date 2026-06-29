import unittest

from utils.messages import split_message


class SplitMessageTests(unittest.TestCase):
    def test_short_text_is_not_split(self) -> None:
        self.assertEqual(split_message("Короткий текст"), ["Короткий текст"])

    def test_long_text_is_split(self) -> None:
        parts = split_message("abcdefghij" * 13, max_length=50)

        self.assertGreater(len(parts), 1)

    def test_split_preserves_text_and_limit(self) -> None:
        text = "abcdefghij" * 13
        parts = split_message(text, max_length=50)

        self.assertTrue(all(len(part) <= 50 for part in parts))
        self.assertEqual("".join(parts), text)


if __name__ == "__main__":
    unittest.main()
