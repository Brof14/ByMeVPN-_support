import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger("user_activity")


class LoggingMiddleware(BaseMiddleware):
    """
    Logs every incoming user message to the console.

    Format:
        Пользователь Иван Петров (@username) с ID: 123456789 написал: текст
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            u = event.from_user

            first  = u.first_name or ""
            last   = u.last_name  or ""          # None-safe
            name   = f"{first} {last}".strip()
            handle = f"@{u.username}" if u.username else "без username"

            # Represent any content type as a readable string
            if event.text:
                content = event.text
            elif event.caption:
                content = f"[медиа] {event.caption}"
            elif event.photo:
                content = "[фото]"
            elif event.video:
                content = "[видео]"
            elif event.document:
                content = "[документ]"
            elif event.voice:
                content = "[голосовое]"
            elif event.audio:
                content = "[аудио]"
            elif event.sticker:
                content = f"[стикер: {event.sticker.emoji or '?'}]"
            else:
                content = f"[{event.content_type}]"

            logger.info(
                "Пользователь %s (%s) с ID: %s написал: %s",
                name, handle, u.id, content,
            )

        return await handler(event, data)
