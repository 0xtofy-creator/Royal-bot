from aiogram.fsm.state import StatesGroup, State


class LeadStates(StatesGroup):
    waiting_for_text = State()
