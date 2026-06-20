from aiogram.fsm.state import State, StatesGroup


class VisionStates(StatesGroup):
    waiting_for_image = State()
