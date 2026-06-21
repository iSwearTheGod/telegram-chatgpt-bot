import unittest

from prompts import (
    build_quiz_prompt,
    build_resume_user_prompt,
    build_translation_system_prompt,
)


class PromptBuilderTests(unittest.TestCase):
    def test_quiz_prompt_contains_topic_data(self) -> None:
        prompt = build_quiz_prompt("Тема", "Описание")

        self.assertIn("Тема", prompt)
        self.assertIn("Описание", prompt)

    def test_translation_prompt_contains_target_language(self) -> None:
        prompt = build_translation_system_prompt("тестовый язык")

        self.assertIn("тестовый язык", prompt)

    def test_resume_prompt_keeps_sections_separate(self) -> None:
        prompt = build_resume_user_prompt(
            education="Учебные данные",
            experience="Рабочие данные",
            skills="Навыки",
        )

        self.assertIn("Образование:\nУчебные данные", prompt)
        self.assertIn("Опыт работы:\nРабочие данные", prompt)
        self.assertIn("Навыки:\nНавыки", prompt)


if __name__ == "__main__":
    unittest.main()
