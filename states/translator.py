from aiogram.fsm.state import State, StatesGroup


class TranslatorStates(StatesGroup):
    choosing_language = State()
    waiting_for_text = State()
