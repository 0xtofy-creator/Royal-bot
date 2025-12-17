from aiogram.fsm.state import StatesGroup, State


class ProblemState(StatesGroup):
    waiting_text = State()
