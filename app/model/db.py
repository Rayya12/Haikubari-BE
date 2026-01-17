import uuid
from fastapi.params import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import Column, ForeignKey, String,Text,DateTime,Enum,Numeric,Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase,relationship
from typing import AsyncGenerator
import datetime
import os
import enum
import dotenv

dotenv.load_dotenv()
DATABASE_URL = os.getenv("POSTGRES_URL_NON_POOLING")

DATABASE_URL = DATABASE_URL.replace(
    "postgres://",
    "postgresql+asyncpg://"
)

DATABASE_URL = DATABASE_URL.split("?")[0]

class Base(DeclarativeBase):
    pass

class RoleEnum(enum.Enum):
    common = "common"
    watcher = "watcher"
    admin = "admin"
    
class WathcherEnum(enum.Enum):
    pending = "pending"
    suspended = "suspended"
    accepted = "accepted"

class User(Base):
    __tablename__ = "users"
    
    # Important fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(RoleEnum,name="role_enum"), default=RoleEnum.common, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verfied = Column(Boolean, default=False)
    status = Column(Enum(WathcherEnum,name="watcher_enum"),default=WathcherEnum.pending,nullable=False)
    
    # Additional profile fields
    photo_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)

    bio = Column(Text, nullable=True)
    age = Column(Numeric, nullable=True)
    address = Column(String, nullable=True)
    
    haikus = relationship("Haiku",back_populates="user",cascade="all, delete-orphan",passive_deletes=True)
    
class Haiku(Base):
    __tablename__ = "haikus"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # many-to-one: Haiku -> User
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    content = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    likes = Column(Numeric, default=0)
    
    user = relationship("User", back_populates="haikus")
    
class OTP(Base):
    __tablename__ = "otps"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"))
    code = Column(String,nullable=False)
    expired_at = Column(DateTime,nullable=False)
    
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session() as session:
        yield session
        
async def get_user_db(session:AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session,User)
