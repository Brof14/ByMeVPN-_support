from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.common import send_main_menu

router = Router()


@router.message()
async def catch_all(message: Message, state: FSMContext) -> None:
    """
    Catches every message that no other handler claimed:
    unknown commands (/abc, /xyz…), arbitrary text, etc.
    Responds exactly like /start.

    IMPORTANT: this router must be included LAST in main.py so it
    never shadows any real handler registered before it.
    """
    await send_main_menu(message, state)
