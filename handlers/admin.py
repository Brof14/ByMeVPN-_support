from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS
from database.repository import add_message, get_ticket, set_ban
from handlers.utils import extract_file
from keyboards.user_kb import reply_to_support_kb
from states import AdminFlow

router = Router()

_CAPTION_TYPES = {"photo", "video", "document", "audio", "voice", "animation"}


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ── Initiate reply ────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_reply:"))
async def cb_admin_reply(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа.", show_alert=True)

    _, ticket_id_str, user_tg_id_str = callback.data.split(":")
    ticket_id  = int(ticket_id_str)
    user_tg_id = int(user_tg_id_str)

    await state.set_state(AdminFlow.replying)
    await state.update_data(ticket_id=ticket_id, user_tg_id=user_tg_id)
    await callback.answer()
    await callback.message.answer(
        f"✉️ Введите ответ на <b>тикет #{ticket_id}</b>:"
    )


# ── Send reply to user ────────────────────────────────────────────────────────

@router.message(AdminFlow.replying)
async def handle_admin_reply(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        return

    data       = await state.get_data()
    ticket_id  = data["ticket_id"]
    user_tg_id = data["user_tg_id"]

    ticket = await get_ticket(ticket_id)
    if not ticket:
        await state.clear()
        await message.answer("Тикет не найден.")
        return

    file_id, file_type = extract_file(message)
    await add_message(ticket_id, True, message.text or message.caption, file_id, file_type)
    await state.clear()

    divider = "─" * 30
    header  = f"💬 <b>Ответ поддержки — тикет #{ticket_id}</b>\n{divider}\n"
    kb      = reply_to_support_kb(ticket_id)

    try:
        if message.text:
            await message.bot.send_message(user_tg_id, header + message.text, reply_markup=kb)

        elif file_type in _CAPTION_TYPES:
            original = message.caption or ""
            caption  = (header + original) if original else header.rstrip("\n")
            await message.bot.copy_message(
                chat_id=user_tg_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await message.bot.send_message(user_tg_id, header.rstrip("\n"), reply_markup=kb)
            await message.copy_to(user_tg_id)

    except Exception:
        await message.answer(
            "⚠️ Не удалось доставить ответ — пользователь, вероятно, заблокировал бота."
        )
        return

    await message.answer(f"✅ Ответ по тикету <b>#{ticket_id}</b> отправлен.")


# ── Ban via inline button ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_ban:"))
async def cb_admin_ban(callback: CallbackQuery) -> None:
    if not _is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа.", show_alert=True)

    user_tg_id = int(callback.data.split(":")[1])
    user = await set_ban(user_tg_id, True)

    if user:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await callback.answer(
            f"🚫 {user.first_name} (ID {user_tg_id}) заблокирован.", show_alert=True
        )
    else:
        await callback.answer("Пользователь не найден.", show_alert=True)


# ── /ban and /unban commands ──────────────────────────────────────────────────

@router.message(Command("ban"))
async def cmd_ban(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].lstrip("-").isdigit():
        await message.answer("Использование: <code>/ban &lt;user_id&gt;</code>")
        return

    user = await set_ban(int(parts[1]), True)
    if user:
        await message.answer(
            f"🚫 Пользователь <b>{user.first_name}</b> "
            f"(<code>{user.tg_id}</code>) заблокирован."
        )
    else:
        await message.answer(f"Пользователь <code>{parts[1]}</code> не найден.")


@router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2 or not parts[1].lstrip("-").isdigit():
        await message.answer("Использование: <code>/unban &lt;user_id&gt;</code>")
        return

    user = await set_ban(int(parts[1]), False)
    if user:
        await message.answer(
            f"✅ Пользователь <b>{user.first_name}</b> "
            f"(<code>{user.tg_id}</code>) разблокирован."
        )
    else:
        await message.answer(f"Пользователь <code>{parts[1]}</code> не найден.")


# ── /help for admins ──────────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    if not _is_admin(message.from_user.id):
        return

    await message.answer(
        "<b>👮 Команды администратора</b>\n\n"
        "/ban <code>&lt;user_id&gt;</code> — заблокировать пользователя\n"
        "/unban <code>&lt;user_id&gt;</code> — разблокировать пользователя\n"
        "/help — это сообщение\n\n"
        "<i>Кнопки [✉️ Ответить] и [🚫 Заблокировать] доступны прямо в уведомлениях о тикетах.</i>"
    )
