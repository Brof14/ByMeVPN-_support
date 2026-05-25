from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import ADMIN_IDS
from database.repository import get_user_by_tg_id


class BanCheckMiddleware(BaseMiddleware):
    """Silently drops incoming messages from banned users (admins are exempt)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            if event.from_user.id not in ADMIN_IDS:
                user = await get_user_by_tg_id(event.from_user.id)
                if user and user.is_banned:
                    await event.answer("🚫 Вы заблокированы и не можете отправлять запросы.")
                    return
        return await handler(event, data)
