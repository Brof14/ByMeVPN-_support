from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.repository import get_or_create_user
from keyboards.user_kb import MAIN_MENU

router = Router()


async def send_main_menu(message: Message, state: FSMContext) -> None:
    """
    Shared entry point: resets state, upserts the user, shows the main menu.
    Called by /start and the catch-all fallback handler.
    """
    await state.clear()
    await get_or_create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.answer(
        "👋 Добро пожаловать в поддержку <b>ByMeVPN</b>!\n\n"
        "Выберите действие ниже:",
        reply_markup=MAIN_MENU,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await send_main_menu(message, state)
