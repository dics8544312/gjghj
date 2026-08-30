"""
Обработчик команд для родителей
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from services import UserService, StatisticsService
from keyboards import (
    get_parent_menu, 
    get_cancel_keyboard_inline, 
    get_child_stats_keyboard,
    get_settings_keyboard,
    get_change_role_keyboard
)
from models.user import UserRole
from config import settings

router = Router(name="parent")


class ParentStates(StatesGroup):
    """Состояния родителя"""
    waiting_child_username = State()


@router.callback_query(F.data == "find_child")
async def find_child(callback: CallbackQuery, state: FSMContext):
    """Начало поиска ребенка"""
    await callback.message.edit_text(
        "📌 Поиск ребенка\n\n"
        "Введите Telegram username вашего ребенка (например: @username или username):",
        reply_markup=get_cancel_keyboard_inline()
    )
    await state.set_state(ParentStates.waiting_child_username)
    await callback.answer()


@router.message(ParentStates.waiting_child_username, F.text != "❌ Отмена")
async def process_child_username(message: Message, session: AsyncSession, state: FSMContext):
    """Обработка введенного username ребенка"""
    parent_id = message.from_user.id
    username = message.text.strip().lstrip('@')
    
    # Ищем ребенка по username
    child = await UserService.get_user_by_username(session, username)
    
    if not child:
        await message.answer(
            f"❌ Пользователь с username @{username} не найден.\n\n"
            f"Убедитесь, что:\n"
            f"• Username указан правильно\n"
            f"• Ребенок уже зарегистрирован в боте\n\n"
            f"Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard_inline()
        )
        return
    
    # Проверяем что это ученик
    if child.role != UserRole.STUDENT:
        await message.answer(
            f"❌ Пользователь @{username} не является учеником.\n\n"
            f"Можно привязать только учеников.\n\n"
            f"Попробуйте другой username:",
            reply_markup=get_cancel_keyboard_inline()
        )
        return
    
    # Создаем связь родитель-ребенок
    relation = await UserService.link_parent_child(session, parent_id, child.telegram_id)
    await session.commit()
    
    is_admin = parent_id in settings.admin_ids_list
    
    await message.answer(
        f"✅ Ребенок успешно добавлен!\n\n"
        f"👤 Имя: {child.full_name}\n"
        f"🎓 Класс: {child.class_number}\n\n"
        f"Теперь вы можете просматривать его статистику в разделе \"👨‍👧 Мои дети\"",
        reply_markup=get_parent_menu(is_admin)
    )
    await state.clear()


@router.callback_query(F.data == "my_children")
async def show_children(callback: CallbackQuery, session: AsyncSession):
    """Показать список детей родителя"""
    parent_id = callback.from_user.id
    
    # Получаем детей
    children = await UserService.get_children(session, parent_id)
    
    if not children:
        await callback.message.edit_text(
            "📝 У вас пока нет привязанных детей.\n\n"
            "Используйте \"📌 Найти ребенка\" чтобы добавить ребенка.",
            reply_markup=get_parent_menu(parent_id in settings.admin_ids_list)
        )
        await callback.answer()
        return
    
    response = "👨‍👧 Ваши дети:\n\n"
    
    for child in children:
        # Получаем статистику ребенка
        stats = await StatisticsService.get_user_progress(session, child.telegram_id)
        
        response += f"👤 {child.full_name}\n"
        response += f"   @{child.username}\n" if child.username else ""
        response += f"   🎓 Класс: {child.class_number}\n"
        response += f"   📝 Решено задач: {stats.get('solved_tasks', 0)}\n"
        response += f"   📈 Успеваемость: {stats.get('success_rate', 0)}%\n"
        response += f"   🕐 Последняя активность: {stats.get('last_activity', 'Нет данных')}\n"
        response += "\n"
    
    await callback.message.edit_text(response, reply_markup=get_parent_menu(parent_id in settings.admin_ids_list))
    await callback.answer()


@router.callback_query(F.data.startswith("child_stats_"))
async def show_child_detailed_stats(callback: CallbackQuery, session: AsyncSession):
    """Показать подробную статистику ребенка"""
    child_id = int(callback.data.split("_")[2])
    parent_id = callback.from_user.id
    
    # Проверяем что ребенок привязан к этому родителю
    children = await UserService.get_children(session, parent_id)
    child = next((c for c in children if c.telegram_id == child_id), None)
    
    if not child:
        await callback.answer("Ошибка: ребенок не найден", show_alert=True)
        return
    
    # Получаем статистику
    stats = await StatisticsService.get_user_progress(session, child_id)
    recent_activity = await StatisticsService.get_recent_activity(session, child_id, 7)
    
    response = (
        f"📊 Подробная статистика\n\n"
        f"👤 {child.full_name}\n"
        f"🎓 Класс: {child.class_number}\n\n"
        f"📝 Всего задач: {stats.get('total_tasks', 0)}\n"
        f"✅ Решено: {stats.get('solved_tasks', 0)}\n"
        f"✓ Правильных ответов: {stats.get('correct_answers', 0)}\n"
        f"✗ Ошибок: {stats.get('mistakes', 0)}\n"
        f"📈 Процент успеха: {stats.get('success_rate', 0)}%\n\n"
        f"📅 За последние 7 дней:\n"
        f"   Решено задач: {recent_activity.get('tasks_completed', 0)}\n"
        f"   Правильных: {recent_activity.get('correct_answers', 0)}\n"
        f"   Успеваемость: {recent_activity.get('success_rate', 0)}%\n"
    )
    
    # Добавляем темы
    topics = stats.get('topics', {})
    if topics:
        response += "\n📚 Изученные темы:\n"
        for topic, count in topics.items():
            if topic:
                response += f"• {topic}: {count} задач\n"
    
    await callback.message.edit_text(response)
    await callback.answer()


@router.callback_query(ParentStates.waiting_child_username, F.data == "cancel_action")
async def cancel_parent_action_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Отмена текущего действия родителя через callback"""
    user_id = callback.from_user.id
    is_admin = user_id in settings.admin_ids_list
    user = await UserService.get_user(session, user_id)
    
    await state.clear()
    await callback.message.edit_text(
        f"Действие отменено.\n\n"
        f"👋 {user.full_name}, выберите действие:",
        reply_markup=get_parent_menu(is_admin)
    )
    await callback.answer("Действие отменено")


@router.message(ParentStates.waiting_child_username, F.text == "❌ Отмена")
async def cancel_parent_action(message: Message, session: AsyncSession, state: FSMContext):
    """Отмена текущего действия родителя через текст"""
    user_id = message.from_user.id
    is_admin = user_id in settings.admin_ids_list
    user = await UserService.get_user(session, user_id)
    
    await state.clear()
    await message.answer(
        f"Действие отменено.\n\n"
        f"👋 {user.full_name}, выберите действие:",
        reply_markup=get_parent_menu(is_admin)
    )



@router.callback_query(F.data == "settings")
async def settings_menu_parent(callback: CallbackQuery, session: AsyncSession):
    """Меню настроек для родителей"""
    user_id = callback.from_user.id
    user = await UserService.get_user(session, user_id)
    
    response = f"⚙️ *Ваш профиль*\n\n"
    response += f"👤 Имя: {user.full_name}\n"
    response += f"📱 Username: @{user.username}\n" if user.username else ""
    response += f"🎭 Роль: Родитель\n\n"
    response += f"🔧 *Настройки:*\n"
    response += f"• Смените роль если хотите стать учеником\n"
    response += f"• При смене на ученика потребуется выбрать класс"
    
    await callback.message.edit_text(
        response, 
        reply_markup=get_settings_keyboard(is_student=False),
        parse_mode="Markdown"
    )
    await callback.answer()
