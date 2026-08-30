"""
Модель пользователя
Хранит информацию об учениках, родителях и администраторах
"""

from sqlalchemy import BigInteger, String, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from database.database import Base


class UserRole(enum.Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    STUDENT = "student"
    PARENT = "parent"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=True)
    class_number: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связь с кодами доступа
    access_codes = relationship("AccessCode", back_populates="user", foreign_keys="AccessCode.activated_by")
    
    # Связь с задачами
    tasks = relationship("Task", back_populates="user")
    
    # Связь с прогрессом
    progress = relationship("Progress", back_populates="user", uselist=False)
    
    # Связи родитель-ребенок (как родитель)
    children = relationship(
        "ParentChild",
        foreign_keys="ParentChild.parent_id",
        back_populates="parent"
    )
    
    # Связи родитель-ребенок (как ребенок)
    parents = relationship(
        "ParentChild",
        foreign_keys="ParentChild.child_id",
        back_populates="child"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, role={self.role})>"
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return f"User {self.telegram_id}"
