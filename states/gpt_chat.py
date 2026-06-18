from aiogram.fsm.state import State, StatesGroup


class GPTChatStates(StatesGroup):
    chatting = State()
