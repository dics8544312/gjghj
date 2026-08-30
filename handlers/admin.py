"""
Обработчик команд для администраторов
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from services import AccessService, UserService, StatisticsService, manual_backup
from keyboards import get_admin_menu, get_codes_admin_menu, get_users_admin_menu, get_cancel_keyboard_inline
from models import User
from config import settings

router = Router(name="admin")


class AdminStates(StatesGroup):
    """Состояния администратора"""
    waiting_code_name = State()
    waiting_code_duration = State()
    waiting_code_to_delete = State()


def is_admin(user_id: int) -> bool:
    """Проверка прав администратора"""
    return user_id in settings.admin_ids_list


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Главная админ-панель через callback"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа к админ-панели", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 Админ-панель\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()


@router.message(F.text == "🔧 Админ-панель")
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Главная админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели")
        return
    
    await message.answer(
        "🔧 Админ-панель\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu()
    )


@router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery):
    """Показать главное меню админки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 Админ-панель\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()


# ===== УПРАВЛЕНИЕ КОДАМИ ДОСТУПА =====

@router.callback_query(F.data == "admin_codes")
async def codes_menu(callback: CallbackQuery):
    """Меню управления кодами"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔑 Управление кодами доступа\n\n"
        "Выберите действие:",
        reply_markup=get_codes_admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "code_create")
async def start_code_creation(callback: CallbackQuery, state: FSMContext):
    """Начало создания кода"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.answer(
        "➕ Создание нового кода\n\n"
        "Введите название кода (например: MATH2026, PROMO30):",
        reply_markup=get_cancel_keyboard_inline()
    )
    await state.set_state(AdminStates.waiting_code_name)
    await callback.answer()


@router.message(AdminStates.waiting_code_name, F.text != "❌ Отмена")
async def get_code_name(message: Message, state: FSMContext):
    """Получение названия кода"""
    if not is_admin(message.from_user.id):
        return
    
    code_name = message.text.strip().upper()
    
    # Проверяем длину кода
    if len(code_name) < 4 or len(code_name) > 20:
        await message.answer(
            "❌ Код должен быть от 4 до 20 символов.\n\n"
            "Попробуйте еще раз:",
            reply_markup=get_cancel_keyboard_inline()
        )
        return
    
    await state.update_data(code_name=code_name)
    await message.answer(
        f"Код: {code_name}\n\n"
        f"Теперь введите срок действия в днях (например: 30, 90, 365):",
        reply_markup=get_cancel_keyboard_inline()
    )
    await state.set_state(AdminStates.waiting_code_duration)


@router.message(AdminStates.waiting_code_duration, F.text != "❌ Отмена")
async def create_code(message: Message, session: AsyncSession, state: FSMContext):
    """Создание кода"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        duration = int(message.text.strip())
        if duration <= 0 or duration > 3650:
            raise ValueError()
    except ValueError:
        await message.answer(
            "❌ Введите корректное количество дней (от 1 до 3650):",
            reply_markup=get_cancel_keyboard_inline()
        )
        return
    
    data = await state.get_data()
    code_name = data.get("code_name")
    
    # Проверяем существование кода
    existing_code = await AccessService.get_code(session, code_name)
    if existing_code:
        await message.answer(
            f"❌ Код {code_name} уже существует.\n\n"
            f"Введите другое название:",
            reply_markup=get_cancel_keyboard_inline()
        )
        await state.set_state(AdminStates.waiting_code_name)
        return
    
    # Создаем код
    code = await AccessService.create_access_code(
        session,
        code_name,
        duration,
        message.from_user.id
    )
    await session.commit()
    
    await message.answer(
        f"✅ Код успешно создан!\n\n"
        f"🔑 Код: {code.code}\n"
        f"📅 Срок действия: {code.duration_days} дней\n\n"
        f"Отправьте этот код пользователю для активации."
    )
    
    await state.clear()


@router.callback_query(F.data == "code_list_active")
async def list_active_codes(callback: CallbackQuery, session: AsyncSession):
    """Список активных кодов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    codes = await AccessService.get_active_codes(session)
    
    if not codes:
        await callback.answer("Нет активных кодов", show_alert=True)
        return
    
    response = "🔑 Активные коды:\n\n"
    for code in codes:
        response += f"• {code.code}\n"
        response += f"  Срок: {code.duration_days} дней\n"
        response += f"  Создан: {code.created_at.strftime('%d.%m.%Y')}\n\n"
    
    await callback.message.edit_text(response, reply_markup=get_codes_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "code_list_all")
async def list_all_codes(callback: CallbackQuery, session: AsyncSession):
    """Список всех кодов"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    codes = await AccessService.get_all_codes(session)
    
    if not codes:
        await callback.answer("Нет кодов", show_alert=True)
        return
    
    response = "📜 Все коды:\n\n"
    for code in codes[:20]:  # Показываем первые 20
        status = "✅ Активен" if code.is_active else "❌ Использован"
        response += f"• {code.code} - {status}\n"
        response += f"  Срок: {code.duration_days} дней\n"
        
        if code.activated_by:
            response += f"  Активирован: {code.activated_at.strftime('%d.%m.%Y')}\n"
            if code.expires_at:
                response += f"  Истекает: {code.expires_at.strftime('%d.%m.%Y')}\n"
        
        response += "\n"
    
    if len(codes) > 20:
        response += f"\n... и еще {len(codes) - 20} кодов"
    
    await callback.message.edit_text(response, reply_markup=get_codes_admin_menu())
    await callback.answer()


# ===== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ =====

@router.callback_query(F.data == "admin_users")
async def users_menu(callback: CallbackQuery, session: AsyncSession):
    """Меню управления пользователями - показываем всех с username"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # Получаем всех пользователей
    result = await session.execute(
        select(User).order_by(User.created_at.desc()).limit(20)
    )
    users = result.scalars().all()
    
    if not users:
        await callback.answer("Нет пользователей в базе", show_alert=True)
        return
    
    response = f"👥 Последние пользователи ({len(users)}):\n\n"
    
    for user in users:
        response += f"👤 {user.full_name}\n"
        
        if user.username:
            response += f"   @{user.username}\n"
        else:
            response += f"   ⚠️ НЕТ USERNAME\n"
        
        response += f"   ID: {user.telegram_id}\n"
        response += f"   Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        
        # Проверяем доступ
        active_code = await AccessService.get_user_active_code(session, user.telegram_id)
        if active_code:
            days_left = (active_code.expires_at - datetime.utcnow()).days
            response += f"   ✅ Доступ: {days_left} дней (до {active_code.expires_at.strftime('%d.%m.%Y')})\n"
        else:
            response += f"   ❌ Нет доступа\n"
        
        response += "\n"
    
    await callback.message.edit_text(
        response,
        reply_markup=get_users_admin_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "users_students")
async def list_students(callback: CallbackQuery, session: AsyncSession):
    """Список учеников"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    students = await UserService.get_all_students(session)
    
    if not students:
        await callback.answer("Нет учеников", show_alert=True)
        return
    
    response = f"👨‍🎓 Ученики ({len(students)}):\n\n"
    
    for student in students[:15]:  # Показываем первых 15
        response += f"👤 {student.full_name}\n"
        response += f"   ID: {student.telegram_id}\n"
        
        if student.username:
            response += f"   @{student.username}\n"
        
        response += f"   🎓 Класс: {student.class_number}\n"
        response += f"   📅 Регистрация: {student.created_at.strftime('%d.%m.%Y')}\n"
        
        # Проверяем подписку
        active_code = await AccessService.get_user_active_code(session, student.telegram_id)
        if active_code:
            response += f"   ✅ Подписка до: {active_code.expires_at.strftime('%d.%m.%Y')}\n"
        else:
            response += f"   ❌ Подписка неактивна\n"
        
        response += "\n"
    
    if len(students) > 15:
        response += f"\n... и еще {len(students) - 15} учеников"
    
    await callback.message.edit_text(response, reply_markup=get_users_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "users_parents")
async def list_parents(callback: CallbackQuery, session: AsyncSession):
    """Список родителей"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    parents = await UserService.get_all_parents(session)
    
    if not parents:
        await callback.answer("Нет родителей", show_alert=True)
        return
    
    response = f"👨‍👩‍👦 Родители ({len(parents)}):\n\n"
    
    for parent in parents[:15]:
        response += f"👤 {parent.full_name}\n"
        response += f"   ID: {parent.telegram_id}\n"
        
        if parent.username:
            response += f"   @{parent.username}\n"
        
        response += f"   📅 Регистрация: {parent.created_at.strftime('%d.%m.%Y')}\n"
        
        # Количество детей
        children = await UserService.get_children(session, parent.telegram_id)
        response += f"   👶 Детей: {len(children)}\n\n"
    
    if len(parents) > 15:
        response += f"\n... и еще {len(parents) - 15} родителей"
    
    await callback.message.edit_text(response, reply_markup=get_users_admin_menu())
    await callback.answer()


# ===== СТАТИСТИКА =====

@router.callback_query(F.data == "admin_stats")
async def show_statistics(callback: CallbackQuery, session: AsyncSession):
    """Глобальная статистика"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    stats = await StatisticsService.get_global_statistics(session)
    
    response = (
        f"📊 Общая статистика проекта\n\n"
        f"👨‍🎓 Учеников: {stats.get('students')}\n"
        f"👨‍👩‍👦 Родителей: {stats.get('parents')}\n"
        f"✅ Активных подписок: {stats.get('active_subscriptions')}\n"
        f"📝 Всего решено задач: {stats.get('total_tasks_solved')}\n\n"
    )
    
    # Распределение по классам
    class_dist = stats.get('class_distribution', {})
    if class_dist:
        response += "🎓 Распределение по классам:\n"
        for class_num in sorted(class_dist.keys()):
            if class_num:
                response += f"   {class_num} класс: {class_dist[class_num]} учеников\n"
    
    await callback.message.edit_text(response, reply_markup=get_admin_menu())
    await callback.answer()


# ===== РЕЗЕРВНОЕ КОПИРОВАНИЕ =====

@router.callback_query(F.data == "admin_backup")
async def create_manual_backup(callback: CallbackQuery):
    """Создание резервной копии вручную"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.answer("⏳ Создаю резервную копию...", show_alert=True)
    
    try:
        await manual_backup()
        await callback.message.answer(
            "✅ <b>Резервная копия создана</b>\n\n"
            "Файл отправлен в канал для бэкапов.",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ <b>Ошибка при создании бэкапа</b>\n\n"
            f"Детали: {str(e)[:500]}",
            parse_mode="HTML"
        )


# ===== ОТМЕНА ДЕЙСТВИЙ =====

@router.callback_query(AdminStates.waiting_code_name, F.data == "cancel_action")
@router.callback_query(AdminStates.waiting_code_duration, F.data == "cancel_action")
async def cancel_admin_action_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена действия администратора через callback"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await state.clear()
    await callback.message.edit_text(
        "Действие отменено.\n\n"
        "🔧 Админ-панель\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu()
    )
    await callback.answer("Действие отменено")


@router.message(AdminStates.waiting_code_name, F.text == "❌ Отмена")
@router.message(AdminStates.waiting_code_duration, F.text == "❌ Отмена")
async def cancel_admin_action(message: Message, state: FSMContext):
    """Отмена действия администратора через текст"""
    if not is_admin(message.from_user.id):
        return
    
    await state.clear()
    await message.answer(
        "Действие отменено.\n\n"
        "🔧 Админ-панель\n\n"
        "Выберите раздел:",
        reply_markup=get_admin_menu()
    )
