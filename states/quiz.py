from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    choosing_topic = State()
    waiting_for_answer = State()
    viewing_result = State()
