"""
Сервис для работы с пользователями
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Progress, ParentChild
from models.user import UserRole
from typing import Optional, List


class UserService:
    """Сервис для управления пользователями"""
    
    @staticmethod
    async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID пользователя
            
        Returns:
            Объект User или None
        """
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """
        Получить пользователя по username
        
        Args:
            session: Сессия БД
            username: Username без @
            
        Returns:
            Объект User или None
        """
        # Убираем @ если он есть
        username = username.lstrip('@')
        
        # Ищем БЕЗ учёта регистра используя функцию lower()
        from sqlalchemy import func
        result = await session.execute(
            select(User).where(func.lower(User.username) == func.lower(username))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Создать нового пользователя
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID
            username: Username
            first_name: Имя
            last_name: Фамилия
            
        Returns:
            Созданный пользователь
        """
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        await session.flush()
        return user
    
    @staticmethod
    async def set_user_role(session: AsyncSession, telegram_id: int, role: UserRole) -> User:
        """
        Установить роль пользователя
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID
            role: Роль пользователя
            
        Returns:
            Обновленный пользователь
        """
        user = await UserService.get_user(session, telegram_id)
        if user:
            user.role = role
            await session.flush()
        return user
    
    @staticmethod
    async def set_user_class(session: AsyncSession, telegram_id: int, class_number: int) -> User:
        """
        Установить класс ученика
        
        Args:
            session: Сессия БД
            telegram_id: Telegram ID
            class_number: Номер класса (1-11)
            
        Returns:
            Обновленный пользователь
        """
        user = await UserService.get_user(session, telegram_id)
        if user:
            user.class_number = class_number
            
            # Создаем запись прогресса для ученика если её нет
            progress = await session.execute(
                select(Progress).where(Progress.user_id == user.id)
            )
            if not progress.scalar_one_or_none():
                new_progress = Progress(user_id=user.id)
                session.add(new_progress)
            
            await session.flush()
        return user
    
    @staticmethod
    async def get_all_students(session: AsyncSession) -> List[User]:
        """
        Получить всех учеников
        
        Args:
            session: Сессия БД
            
        Returns:
            Список учеников
        """
        result = await session.execute(
            select(User).where(User.role == UserRole.STUDENT)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_all_parents(session: AsyncSession) -> List[User]:
        """
        Получить всех родителей
        
        Args:
            session: Сессия БД
            
        Returns:
            Список родителей
        """
        result = await session.execute(
            select(User).where(User.role == UserRole.PARENT)
        )
        return result.scalars().all()
    
    @staticmethod
    async def link_parent_child(
        session: AsyncSession,
        parent_id: int,
        child_id: int
    ) -> Optional[ParentChild]:
        """
        Связать родителя и ребенка
        
        Args:
            session: Сессия БД
            parent_id: Telegram ID родителя
            child_id: Telegram ID ребенка
            
        Returns:
            Созданная связь или None если ребенок не найден/не ученик
        """
        # Получаем родителя и ребенка
        parent = await UserService.get_user(session, parent_id)
        child = await UserService.get_user(session, child_id)
        
        # Проверяем что оба существуют и ребенок является учеником
        if not parent or not child or child.role != UserRole.STUDENT:
            return None
        
        # Проверяем что связь еще не существует
        existing = await session.execute(
            select(ParentChild).where(
                ParentChild.parent_id == parent.id,
                ParentChild.child_id == child.id
            )
        )
        if existing.scalar_one_or_none():
            return existing.scalar_one_or_none()
        
        # Создаем связь (используем user.id вместо telegram_id)
        relation = ParentChild(
            parent_id=parent.id,
            child_id=child.id
        )
        session.add(relation)
        await session.flush()
        return relation
    
    @staticmethod
    async def get_children(session: AsyncSession, parent_id: int) -> List[User]:
        """
        Получить детей родителя
        
        Args:
            session: Сессия БД
            parent_id: Telegram ID родителя
            
        Returns:
            Список детей
        """
        # Получаем родителя
        parent = await UserService.get_user(session, parent_id)
        if not parent:
            return []
        
        result = await session.execute(
            select(User).join(
                ParentChild,
                ParentChild.child_id == User.id
            ).where(ParentChild.parent_id == parent.id)
        )
        return result.scalars().all()
