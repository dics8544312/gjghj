"""
Модель связи родитель-ребенок
Хранит отношения между родителями и учениками
"""

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.database import Base


class ParentChild(Base):
    __tablename__ = "parent_child"
    
    __table_args__ = (
        UniqueConstraint('parent_id', 'child_id', name='unique_parent_child'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    child_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи с пользователями
    parent = relationship("User", foreign_keys=[parent_id], back_populates="children")
    child = relationship("User", foreign_keys=[child_id], back_populates="parents")
    
    def __repr__(self):
        return f"<ParentChild(parent_id={self.parent_id}, child_id={self.child_id})>"
