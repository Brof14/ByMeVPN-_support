from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from config import DB_URL
from database.models import Base, Message, Ticket, User

_engine = create_async_engine(DB_URL, echo=False)
_session = async_sessionmaker(_engine, expire_on_commit=False)


async def init_db() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Users ────────────────────────────────────────────────────────────────────

async def get_or_create_user(tg_id: int, username: str | None, first_name: str) -> User:
    async with _session() as s:
        user = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
        if user is None:
            user = User(tg_id=tg_id, username=username, first_name=first_name)
            s.add(user)
        else:
            user.username   = username
            user.first_name = first_name
        await s.commit()
        await s.refresh(user)
        return user


async def get_user_by_tg_id(tg_id: int) -> User | None:
    async with _session() as s:
        return (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()


async def set_ban(tg_id: int, banned: bool) -> User | None:
    async with _session() as s:
        user = (await s.execute(select(User).where(User.tg_id == tg_id))).scalar_one_or_none()
        if user is None:
            return None
        user.is_banned = banned
        await s.commit()
        await s.refresh(user)
        return user


# ── Tickets ──────────────────────────────────────────────────────────────────

async def create_ticket(user_id: int) -> Ticket:
    async with _session() as s:
        ticket = Ticket(user_id=user_id)
        s.add(ticket)
        await s.commit()
        await s.refresh(ticket)
        return ticket


async def get_ticket(ticket_id: int) -> Ticket | None:
    async with _session() as s:
        return (
            await s.execute(
                select(Ticket)
                .options(selectinload(Ticket.user), selectinload(Ticket.messages))
                .where(Ticket.id == ticket_id)
            )
        ).scalar_one_or_none()


async def get_user_tickets(user_tg_id: int) -> list[Ticket]:
    async with _session() as s:
        user = (await s.execute(select(User).where(User.tg_id == user_tg_id))).scalar_one_or_none()
        if user is None:
            return []
        result = await s.execute(
            select(Ticket)
            .options(selectinload(Ticket.messages))
            .where(Ticket.user_id == user.id)
            .order_by(Ticket.id.desc())
            .limit(10)
        )
        return list(result.scalars().all())


# ── Messages ─────────────────────────────────────────────────────────────────

async def add_message(
    ticket_id: int,
    from_admin: bool,
    text: str | None,
    file_id: str | None,
    file_type: str | None,
) -> Message:
    async with _session() as s:
        msg = Message(
            ticket_id=ticket_id,
            from_admin=from_admin,
            text=text,
            file_id=file_id,
            file_type=file_type,
        )
        s.add(msg)
        await s.commit()
        await s.refresh(msg)
        return msg
