from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def ticket_admin_kb(ticket_id: int, user_tg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✉️ Ответить",
            callback_data=f"admin_reply:{ticket_id}:{user_tg_id}",
        ),
        InlineKeyboardButton(
            text="🚫 Заблокировать",
            callback_data=f"admin_ban:{user_tg_id}",
        ),
    ]])
