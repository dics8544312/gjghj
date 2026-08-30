"""
Клавиатуры для бота
"""

from .main_keyboards import (
    get_start_keyboard,
    get_role_selection_keyboard,
    get_class_selection_keyboard,
    get_student_menu,
    get_parent_menu,
    get_admin_menu,
    get_cancel_keyboard_inline,
    get_solve_task_keyboard,
    get_codes_admin_menu,
    get_users_admin_menu,
    get_child_stats_keyboard,
    get_confirmation_keyboard,
    get_user_management_keyboard,
    get_support_keyboard,
    get_settings_keyboard,
    get_change_role_keyboard,
    remove_keyboard
)

__all__ = [
    "get_start_keyboard",
    "get_role_selection_keyboard",
    "get_class_selection_keyboard",
    "get_student_menu",
    "get_parent_menu",
    "get_admin_menu",
    "get_cancel_keyboard_inline",
    "get_solve_task_keyboard",
    "get_codes_admin_menu",
    "get_users_admin_menu",
    "get_child_stats_keyboard",
    "get_confirmation_keyboard",
    "get_user_management_keyboard",
    "get_support_keyboard",
    "get_settings_keyboard",
    "get_change_role_keyboard",
    "remove_keyboard"
]
