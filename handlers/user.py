from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database.repository import (
    add_message,
    create_ticket,
    get_or_create_user,
    get_ticket,
    get_user_tickets,
)
from handlers.utils import extract_file, notify_admins
from keyboards.user_kb import MAIN_MENU, add_to_ticket_kb, reply_to_support_kb
from states import UserFlow

router = Router()


# ── Main-menu reply buttons (always accessible, clear any active state) ──────

@router.message(F.text == "📝 Написать запрос")
async def btn_new_request(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(UserFlow.creating)
    await message.answer(
        "✏️ Опишите вашу проблему.\n"
        "Можно отправить текст, фото, видео или документ."
    )


@router.message(F.text == "📂 Мои запросы")
async def btn_my_tickets(message: Message, state: FSMContext) -> None:
    await state.clear()
    tickets = await get_user_tickets(message.from_user.id)

    if not tickets:
        await message.answer("У вас пока нет запросов.", reply_markup=MAIN_MENU)
        return

    status_icon = lambda t: "🟢" if t.status == "open" else "🔴"
    date_fmt    = lambda t: t.created_at.strftime("%d.%m.%Y") if t.created_at else "—"

    lines = ["<b>📂 Ваши запросы:</b>\n"]
    for t in tickets:
        lines.append(
            f"{status_icon(t)} <b>#{t.id}</b>  ·  {len(t.messages)} сообщ.  ·  {date_fmt(t)}"
        )

    await message.answer("\n".join(lines), reply_markup=MAIN_MENU)


# ── Creating a new ticket ─────────────────────────────────────────────────────

@router.message(UserFlow.creating)
async def handle_new_ticket(message: Message, state: FSMContext) -> None:
    user = await get_or_create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    ticket   = await create_ticket(user.id)
    file_id, file_type = extract_file(message)
    await add_message(ticket.id, False, message.text or message.caption, file_id, file_type)
    await state.clear()

    await message.answer(
        f"✅ <b>Запрос #{ticket.id} создан.</b>\n"
        "Поддержка ответит в ближайшее время.",
        reply_markup=add_to_ticket_kb(ticket.id),
    )

    full_ticket = await get_ticket(ticket.id)
    await notify_admins(message.bot, full_ticket, user, message, "new")


# ── Adding content to an existing ticket ─────────────────────────────────────

@router.callback_query(F.data.startswith("add:"))
async def cb_add_to_ticket(callback: CallbackQuery, state: FSMContext) -> None:
    ticket_id = int(callback.data.split(":")[1])
    await state.set_state(UserFlow.adding)
    await state.update_data(ticket_id=ticket_id)
    await callback.answer()
    await callback.message.answer(
        f"📎 Отправьте дополнение к запросу <b>#{ticket_id}</b>:"
    )


@router.message(UserFlow.adding)
async def handle_add_to_ticket(message: Message, state: FSMContext) -> None:
    data      = await state.get_data()
    ticket_id = data["ticket_id"]

    ticket = await get_ticket(ticket_id)
    if not ticket:
        await state.clear()
        await message.answer("Запрос не найден.", reply_markup=MAIN_MENU)
        return

    file_id, file_type = extract_file(message)
    await add_message(ticket_id, False, message.text or message.caption, file_id, file_type)
    await state.clear()

    user = await get_or_create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer(
        f"📎 Дополнение к запросу <b>#{ticket_id}</b> отправлено.",
        reply_markup=add_to_ticket_kb(ticket_id),
    )
    await notify_admins(message.bot, ticket, user, message, "add")


# ── Replying to a support response ────────────────────────────────────────────

@router.callback_query(F.data.startswith("user_reply:"))
async def cb_user_reply(callback: CallbackQuery, state: FSMContext) -> None:
    ticket_id = int(callback.data.split(":")[1])
    await state.set_state(UserFlow.replying)
    await state.update_data(ticket_id=ticket_id)
    await callback.answer()
    await callback.message.answer(
        f"✍️ Введите ответ по запросу <b>#{ticket_id}</b>:"
    )


@router.message(UserFlow.replying)
async def handle_user_reply(message: Message, state: FSMContext) -> None:
    data      = await state.get_data()
    ticket_id = data["ticket_id"]

    ticket = await get_ticket(ticket_id)
    if not ticket:
        await state.clear()
        await message.answer("Запрос не найден.", reply_markup=MAIN_MENU)
        return

    file_id, file_type = extract_file(message)
    await add_message(ticket_id, False, message.text or message.caption, file_id, file_type)
    await state.clear()

    user = await get_or_create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )

    await message.answer(
        f"✅ Ответ по запросу <b>#{ticket_id}</b> отправлен.",
        reply_markup=reply_to_support_kb(ticket_id),
    )
    await notify_admins(message.bot, ticket, user, message, "reply")
