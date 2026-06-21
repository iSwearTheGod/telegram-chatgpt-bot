import unittest

from handlers.quiz import validate_question_data
from services.openai_service import OpenAIServiceError


class QuizQuestionValidationTests(unittest.TestCase):
    def test_valid_question_is_normalized(self) -> None:
        result = validate_question_data(
            {
                "question": "  Вопрос?  ",
                "correct_answer": "  Ответ  ",
                "explanation": "  Пояснение  ",
            }
        )

        self.assertEqual(
            result,
            {
                "question": "Вопрос?",
                "correct_answer": "Ответ",
                "explanation": "Пояснение",
            },
        )

    def test_incomplete_question_is_rejected(self) -> None:
        with self.assertLogs("handlers.quiz", level="ERROR"):
            with self.assertRaises(OpenAIServiceError):
                validate_question_data(
                    {
                        "question": "Вопрос?",
                        "correct_answer": "",
                        "explanation": "Пояснение",
                    }
                )


if __name__ == "__main__":
    unittest.main()
