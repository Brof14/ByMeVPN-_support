from aiogram import Bot
from aiogram.types import Message as TgMessage

from config import ADMIN_IDS
from database.models import Ticket, User
from keyboards.admin_kb import ticket_admin_kb

# Media types that support inline captions
_CAPTION_TYPES = {"photo", "video", "document", "audio", "voice", "animation"}


def extract_file(msg: TgMessage) -> tuple[str | None, str | None]:
    """Return (file_id, file_type) from a Telegram message, or (None, None)."""
    if msg.photo:
        return msg.photo[-1].file_id, "photo"
    if msg.video:
        return msg.video.file_id, "video"
    if msg.document:
        return msg.document.file_id, "document"
    if msg.audio:
        return msg.audio.file_id, "audio"
    if msg.voice:
        return msg.voice.file_id, "voice"
    if msg.animation:
        return msg.animation.file_id, "animation"
    if msg.sticker:
        return msg.sticker.file_id, "sticker"
    return None, None


async def notify_admins(
    bot: Bot,
    ticket: Ticket,
    user: User,
    tg_msg: TgMessage,
    label: str,  # "new" | "add" | "reply"
) -> None:
    """Send a formatted ticket notification to every admin in ADMIN_IDS."""
    icons = {"new": "🆕", "add": "📎", "reply": "💬"}
    icon  = icons.get(label, "📩")

    name_link    = f"<a href='tg://user?id={user.tg_id}'>{user.first_name}</a>"
    username_tag = f" (@{user.username})" if user.username else ""
    divider      = "─" * 30

    header = (
        f"{icon} <b>Тикет #{ticket.id}</b>  ·  {name_link}{username_tag}\n"
        f"{divider}\n"
    )

    _, file_type = extract_file(tg_msg)
    kb = ticket_admin_kb(ticket.id, user.tg_id)

    for admin_id in ADMIN_IDS:
        try:
            if tg_msg.text:
                await bot.send_message(admin_id, header + tg_msg.text, reply_markup=kb)

            elif file_type in _CAPTION_TYPES:
                original = tg_msg.caption or ""
                caption  = (header + original) if original else header.rstrip("\n")
                await bot.copy_message(
                    chat_id=admin_id,
                    from_chat_id=tg_msg.chat.id,
                    message_id=tg_msg.message_id,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=kb,
                )
            else:
                # Sticker / video_note / other non-caption types
                await bot.send_message(admin_id, header.rstrip("\n"), reply_markup=kb)
                await tg_msg.copy_to(admin_id)

        except Exception:
            pass  # Skip unreachable admin without crashing
