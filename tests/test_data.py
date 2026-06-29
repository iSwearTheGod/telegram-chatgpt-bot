import unittest

from quiz_data import QUIZ_TOPICS
from translator_data import TRANSLATION_LANGUAGES


class QuizTopicsTests(unittest.TestCase):
    def test_all_expected_topics_exist(self) -> None:
        self.assertEqual(
            set(QUIZ_TOPICS),
            {"python", "history", "geography", "movies"},
        )

    def test_topics_have_required_fields(self) -> None:
        for topic_id, topic in QUIZ_TOPICS.items():
            with self.subTest(topic_id=topic_id):
                self.assertEqual(topic["id"], topic_id)
                self.assertTrue(topic["name"].strip())
                self.assertTrue(topic["description"].strip())


class TranslationLanguagesTests(unittest.TestCase):
    def test_all_expected_languages_exist(self) -> None:
        self.assertEqual(
            set(TRANSLATION_LANGUAGES),
            {"english", "russian", "german", "spanish", "french"},
        )

    def test_language_ids_are_unique_and_fields_are_filled(self) -> None:
        internal_ids = []
        for language_id, language in TRANSLATION_LANGUAGES.items():
            with self.subTest(language_id=language_id):
                self.assertEqual(language["id"], language_id)
                self.assertTrue(language["name"].strip())
                self.assertTrue(language["prompt_name"].strip())
                internal_ids.append(language["id"])

        self.assertEqual(len(internal_ids), len(set(internal_ids)))


if __name__ == "__main__":
    unittest.main()
