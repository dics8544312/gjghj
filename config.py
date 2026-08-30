"""
Конфигурация приложения
Загружает настройки из .env файла
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_IDS: str
    ERROR_LOG_CHANNEL_ID: int = None  # ID канала для логов ошибок
    BACKUP_CHANNEL_ID: int = None  # ID канала для резервных копий БД
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "math_tutor"
    DB_USER: str = "postgres"
    DB_PASSWORD: str
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    # Application
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def database_url(self) -> str:
        """Формирует URL для подключения к БД"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Преобразует строку с ID админов в список"""
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",") if admin_id.strip()]


# Создаем глобальный экземпляр настроек
settings = Settings()
