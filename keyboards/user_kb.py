from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="📝 Написать запрос"),
        KeyboardButton(text="📂 Мои запросы"),
    ]],
    resize_keyboard=True,
    is_persistent=True,
)


def add_to_ticket_kb(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Добавить в запрос", callback_data=f"add:{ticket_id}"),
    ]])


def reply_to_support_kb(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✍️ Ответить", callback_data=f"user_reply:{ticket_id}"),
    ]])
