import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from keyboards.resume import RESUME_BUTTON_TEXT, get_resume_exit_keyboard
from states.resume import ResumeStates


logger = logging.getLogger(__name__)
router = Router(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESUME_IMAGE_PATH = PROJECT_ROOT / "assets" / "resume.png"

EDUCATION_PROMPT = (
    "Расскажите об образовании: учебное заведение, специальность, годы "
    "обучения и дополнительное обучение, если оно есть."
)
EXPERIENCE_PROMPT = (
    "Теперь опишите опыт работы: компании, должности, основные задачи и "
    "достижения.\n\nЕсли опыта пока нет, так и напишите."
)
SKILLS_PROMPT = (
    "Перечислите профессиональные и технические навыки, которые нужно "
    "добавить в резюме."
)


async def start_resume(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ResumeStates.waiting_for_education)

    try:
        if not RESUME_IMAGE_PATH.is_file():
            raise FileNotFoundError
        await message.answer_photo(FSInputFile(RESUME_IMAGE_PATH))
    except (OSError, TelegramAPIError) as error:
        logger.error(
            "Не удалось отправить заставку помощника по резюме: %s",
            type(error).__name__,
        )

    await message.answer(
        "Я последовательно запрошу образование, опыт работы и навыки, а "
        "затем помогу составить текстовый шаблон резюме.\n\n"
        f"{EDUCATION_PROMPT}",
        reply_markup=get_resume_exit_keyboard(),
    )


@router.message(Command("resume"))
@router.message(F.text == RESUME_BUTTON_TEXT)
async def handle_resume_start(message: Message, state: FSMContext) -> None:
    await start_resume(message, state)


@router.message(
    ResumeStates.waiting_for_education,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_resume_education(
    message: Message,
    state: FSMContext,
) -> None:
    education = message.text
    if not education or not education.strip():
        await send_empty_message_error(message)
        return

    await state.update_data(education=education.strip())
    await state.set_state(ResumeStates.waiting_for_experience)
    await message.answer(
        EXPERIENCE_PROMPT,
        reply_markup=get_resume_exit_keyboard(),
    )


@router.message(
    ResumeStates.waiting_for_experience,
    F.text,
    ~F.text.startswith("/"),
)
async def handle_resume_experience(
    message: Message,
    state: FSMContext,
) -> None:
    experience = message.text
    if not experience or not experience.strip():
        await send_empty_message_error(message)
        return

    await state.update_data(experience=experience.strip())
    await state.set_state(ResumeStates.waiting_for_skills)
    await message.answer(
        SKILLS_PROMPT,
        reply_markup=get_resume_exit_keyboard(),
    )


async def send_empty_message_error(message: Message) -> None:
    await message.answer(
        "Сообщение не должно быть пустым. Попробуйте ещё раз.",
        reply_markup=get_resume_exit_keyboard(),
    )


@router.message(
    StateFilter(
        ResumeStates.waiting_for_education,
        ResumeStates.waiting_for_experience,
        ResumeStates.waiting_for_skills,
    ),
    ~F.text,
)
async def handle_resume_non_text(message: Message) -> None:
    await message.answer(
        "Отправьте информацию обычным текстовым сообщением.",
        reply_markup=get_resume_exit_keyboard(),
    )
