from aiogram.fsm.state import State, StatesGroup


class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()
