import uuid
import enum
import datetime
import os
import dotenv
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

from sqlalchemy import Column, ForeignKey, String, Text, DateTime, Enum, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DIRECT_URL")


if not DATABASE_URL:
    raise RuntimeError("POSTGRES_URL_NON_POOLING is not set")


class Base(DeclarativeBase):
    pass


class RoleEnum(str, enum.Enum):
    common = "common"
    watcher = "watcher"
    admin = "admin"


class WatcherEnum(str, enum.Enum):
    pending = "pending"
    suspended = "suspended"
    accepted = "accepted"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(RoleEnum, name="role_enum"), default=RoleEnum.common, nullable=False)
    status = Column(Enum(WatcherEnum, name="watcher_enum"), default=WatcherEnum.pending, nullable=False)

    photo_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)

    bio = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    address = Column(String, nullable=True)

    haikus = relationship(
        "Haiku",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    
class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id",ondelete="CASCADE"), nullable=False, index=True),
    haiku_id = Column(UUID(as_uuid=True), ForeignKey("haikus.id",ondelete="CASCADE"),nullable=False, index= True)
    likes = Column(Integer,default=0)
    content = Column(Text,nullable=False)
    
    __table_args__ = (
        CheckConstraint('likes >= 0', name='check_likes_non_negative'),
        CheckConstraint("char_length(content) <= 300",name="content max 300")
    )
    
    user = relationship("User",back_populates="reviews")
    haiku = relationship("Haiku",back_populates="reviews")


class Haiku(Base):
    __tablename__ = "haikus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(15), nullable=False)
    hashigo = Column(String(5), nullable=False)
    nakasichi = Column(String(7), nullable=False)
    shimogo = Column(String(5), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    likes = Column(Integer, default=0)

    user = relationship("User", back_populates="haikus")
    reviews = relationship("Review",back_populates="haiku",cascade="all, delete-orphan",passive_deletes=True)


class OTP(Base):
    __tablename__ = "otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    code = Column(String, nullable=False)
    expired_at = Column(DateTime(timezone=True), nullable=False)


engine = create_async_engine(DATABASE_URL, echo=True,connect_args={
        "statement_cache_size": 0,
    },)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
