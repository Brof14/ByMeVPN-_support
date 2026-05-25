from aiogram.fsm.state import State, StatesGroup


class UserFlow(StatesGroup):
    creating = State()   # Awaiting first message for a new ticket
    adding   = State()   # Awaiting additional message for an existing ticket
    replying = State()   # Awaiting user reply to admin response


class AdminFlow(StatesGroup):
    replying = State()   # Awaiting admin reply to a ticket
