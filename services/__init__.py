"""
Сервисы приложения
"""

from .ai_service import AIService
from .access_service import AccessService
from .statistics_service import StatisticsService
from .user_service import UserService
from .error_logger import ErrorLogger, init_error_logger, log_error
from .backup_service import (
    BackupService,
    init_backup_service,
    get_backup_service,
    start_backup_service,
    stop_backup_service,
    manual_backup
)

__all__ = [
    "AIService", 
    "AccessService", 
    "StatisticsService", 
    "UserService",
    "ErrorLogger",
    "init_error_logger",
    "log_error",
    "BackupService",
    "init_backup_service",
    "get_backup_service",
    "start_backup_service",
    "stop_backup_service",
    "manual_backup"
]
