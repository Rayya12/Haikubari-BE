from sqlalchemy import Column, Enum,String,Text,Integer
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import relationship
from app.model.base import Base
import enum

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
    
    likestable = relationship("Like",back_populates="users",cascade="all, delete-orphan",passive_deletes=True)

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