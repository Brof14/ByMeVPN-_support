from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer,    primary_key=True, autoincrement=True)
    tg_id      = Column(BigInteger, unique=True, index=True, nullable=False)
    username   = Column(String(64),  nullable=True)
    first_name = Column(String(128), nullable=False)
    is_banned  = Column(Boolean,    default=False, nullable=False)
    created_at = Column(DateTime,   server_default=func.now())

    tickets = relationship("Ticket", back_populates="user")


class Ticket(Base):
    __tablename__ = "tickets"

    id         = Column(Integer,   primary_key=True, autoincrement=True)
    user_id    = Column(Integer,   ForeignKey("users.id"), nullable=False)
    status     = Column(String(16), default="open", nullable=False)
    created_at = Column(DateTime,  server_default=func.now())

    user     = relationship("User",    back_populates="tickets")
    messages = relationship("Message", back_populates="ticket", order_by="Message.id")


class Message(Base):
    __tablename__ = "messages"

    id         = Column(Integer,    primary_key=True, autoincrement=True)
    ticket_id  = Column(Integer,    ForeignKey("tickets.id"), nullable=False)
    from_admin = Column(Boolean,    default=False, nullable=False)
    text       = Column(Text,       nullable=True)
    file_id    = Column(String(256), nullable=True)
    file_type  = Column(String(32),  nullable=True)
    created_at = Column(DateTime,   server_default=func.now())

    ticket = relationship("Ticket", back_populates="messages")
