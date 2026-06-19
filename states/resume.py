from aiogram.fsm.state import State, StatesGroup


class ResumeStates(StatesGroup):
    waiting_for_education = State()
    waiting_for_experience = State()
    waiting_for_skills = State()
