# Бот-репетитор по математике

Полноценный коммерческий Telegram-бот для обучения математике учеников 1-11 классов с системой доступа по кодам, ролями пользователей, родительским контролем и AI-обучением.

## 🚀 Возможности

### Для учеников:
- 📚 Решение задач с AI-помощником
- 💡 Получение подсказок и наводящих вопросов
- 📝 Проверка решений
- 📊 Отслеживание прогресса и статистики
- 🎓 Адаптация под класс обучения

### Для родителей:
- 📌 Поиск и привязка детей
- 📊 Просмотр статистики обучения
- 👨‍👧 Мониторинг активности
- 📈 Отчеты об успеваемости

### Для администраторов:
- 🔑 Управление кодами доступа
- 👥 Управление пользователями
- 📊 Глобальная статистика проекта
- ⚙️ Полный контроль над системой

## 📋 Требования

- Python 3.12+
- PostgreSQL 14+
- OpenAI API ключ

## 🛠️ Установка

### 1. Установка Python

**Windows:**
1. Скачайте Python с [python.org](https://www.python.org/downloads/)
2. Запустите установщик
3. ✅ Обязательно отметьте "Add Python to PATH"
4. Нажмите "Install Now"

Проверка установки:
```powershell
python --version
```

### 2. Установка PostgreSQL

**Windows:**
1. Скачайте PostgreSQL с [postgresql.org](https://www.postgresql.org/download/windows/)
2. Запустите установщик
3. Запомните пароль для пользователя `postgres`
4. Порт по умолчанию: 5432

**Создание базы данных:**
```powershell
# Откройте PowerShell от имени администратора
psql -U postgres

# В консоли PostgreSQL:
CREATE DATABASE math_tutor;
\q
```

### 3. Клонирование проекта

```powershell
cd D:\
git clone <repository-url> math-tutor
cd math-tutor
```

### 4. Создание виртуального окружения

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Если возникла ошибка с политикой выполнения:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. Установка зависимостей

```powershell
pip install -r requirements.txt
```

### 6. Настройка конфигурации

Скопируйте файл `.env.example` в `.env`:
```powershell
Copy-Item .env.example .env
```

Откройте `.env` в текстовом редакторе и заполните:

```env
# Telegram Bot Configuration
BOT_TOKEN=ваш_токен_бота_от_@BotFather
ADMIN_IDS=ваш_telegram_id,второй_admin_id

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=math_tutor
DB_USER=postgres
DB_PASSWORD=ваш_пароль_postgresql

# OpenAI Configuration
OPENAI_API_KEY=ваш_ключ_openai
OPENAI_MODEL=gpt-4

# Application Settings
DEBUG=False
```

### 7. Получение Telegram токена

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Укажите имя бота
4. Укажите username бота (должен заканчиваться на `bot`)
5. Скопируйте полученный токен в `.env`

### 8. Получение Telegram ID

1. Найдите [@userinfobot](https://t.me/userinfobot) в Telegram
2. Отправьте `/start`
3. Скопируйте ваш ID в `.env` в параметр `ADMIN_IDS`

### 9. Получение OpenAI API ключа

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Перейдите в раздел API Keys
3. Создайте новый ключ
4. Скопируйте ключ в `.env`
5. Пополните баланс для использования API

### 10. Миграции базы данных

```powershell
# Создание первой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

## 🚀 Запуск бота

```powershell
# Активируйте виртуальное окружение если еще не активировано
.\venv\Scripts\Activate.ps1

# Запустите бота
python main.py
```

Бот запущен! Вы увидите сообщения в консоли:
```
2024-01-01 12:00:00 - math_tutor_bot - INFO - Запуск бота...
2024-01-01 12:00:00 - math_tutor_bot - INFO - База данных инициализирована
2024-01-01 12:00:00 - math_tutor_bot - INFO - Администраторы: [123456789]
2024-01-01 12:00:00 - math_tutor_bot - INFO - Бот успешно запущен!
2024-01-01 12:00:00 - math_tutor_bot - INFO - Бот начал получать обновления
```

## 📱 Использование

### Первый запуск

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Как администратор, вы увидите кнопку "🔧 Админ-панель"

### Создание кодов доступа

1. Нажмите "🔧 Админ-панель"
2. Выберите "🔑 Коды доступа"
3. Нажмите "➕ Создать код"
4. Введите название кода (например: MATH2026)
5. Введите срок действия в днях (например: 30)
6. Отправьте код новому пользователю

### Активация кода пользователем

1. Пользователь запускает бота `/start`
2. Нажимает "🔑 Ввести код доступа"
3. Вводит полученный код
4. Выбирает роль (Ученик/Родитель)
5. Если ученик - выбирает класс
6. Начинает пользоваться ботом

## 📁 Структура проекта

```
bot/
├── main.py                    # Точка входа
├── config.py                  # Конфигурация
├── requirements.txt           # Зависимости
├── .env                       # Переменные окружения
├── alembic.ini               # Настройки Alembic
│
├── database/                  # База данных
│   ├── database.py           # Подключение к БД
│   └── migrations/           # Миграции Alembic
│       ├── env.py
│       └── versions/
│
├── models/                    # Модели SQLAlchemy
│   ├── user.py               # Модель пользователя
│   ├── access_code.py        # Модель кода доступа
│   ├── task.py               # Модель задачи
│   ├── progress.py           # Модель прогресса
│   └── relation.py           # Модель связи родитель-ребенок
│
├── handlers/                  # Обработчики команд
│   ├── start.py              # Регистрация и /start
│   ├── student.py            # Команды ученика
│   ├── parent.py             # Команды родителя
│   └── admin.py              # Команды администратора
│
├── keyboards/                 # Клавиатуры
│   └── main_keyboards.py     # Основные клавиатуры
│
├── services/                  # Бизнес-логика
│   ├── ai_service.py         # Работа с AI
│   ├── access_service.py     # Управление доступом
│   ├── statistics.py         # Статистика
│   └── user_service.py       # Управление пользователями
│
├── middlewares/               # Middleware
│   ├── access_middleware.py  # Проверка доступа
│   └── db_middleware.py      # Сессии БД
│
└── utils/                     # Утилиты
    └── logger.py             # Логирование
```

## 🔧 Команды бота

### Общие команды:
- `/start` - Запуск бота и регистрация

### Для администраторов:
- `/admin` - Открыть админ-панель
- Кнопка "🔧 Админ-панель" в главном меню

## 📊 База данных

### Таблицы:

**users** - Пользователи
- id, telegram_id, username, first_name, last_name
- role (admin/student/parent)
- class_number, created_at

**access_codes** - Коды доступа
- id, code, duration_days
- created_by, activated_by
- is_active, created_at, activated_at, expires_at

**tasks** - Задачи
- id, user_id, task_text
- topic, difficulty
- student_answer, is_correct
- ai_explanation, created_at, completed_at

**progress** - Прогресс учеников
- id, user_id
- total_tasks, solved_tasks
- correct_answers, mistakes
- last_activity, created_at

**parent_child** - Связи родитель-ребенок
- id, parent_id, child_id, created_at

## 🔒 Безопасность

- ✅ Проверка доступа перед каждым действием
- ✅ Хранение секретов в .env
- ✅ Права администратора по Telegram ID
- ✅ Защита от повторного использования кодов
- ✅ Автоматическая проверка срока действия подписки

## 🐛 Отладка

Включите режим отладки в `.env`:
```env
DEBUG=True
```

Проверьте логи в консоли для диагностики проблем.

## 📝 Частые проблемы

### Ошибка подключения к БД
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Решение:** Проверьте что PostgreSQL запущен и данные в `.env` корректны

### Ошибка с токеном бота
```
aiogram.exceptions.TelegramUnauthorizedError: Unauthorized
```
**Решение:** Проверьте что `BOT_TOKEN` в `.env` правильный

### Ошибка OpenAI API
```
openai.error.AuthenticationError
```
**Решение:** Проверьте `OPENAI_API_KEY` и баланс аккаунта

### Не видно кнопки админ-панели
**Решение:** Убедитесь что ваш Telegram ID указан в `ADMIN_IDS` в `.env`

## 🚀 Развертывание в продакшн

### На VPS (Ubuntu/Debian):

1. **Установите зависимости:**
```bash
sudo apt update
sudo apt install python3.12 python3-pip postgresql nginx
```

2. **Клонируйте проект:**
```bash
git clone <repo> /opt/math-tutor-bot
cd /opt/math-tutor-bot
```

3. **Создайте виртуальное окружение:**
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Настройте PostgreSQL:**
```bash
sudo -u postgres psql
CREATE DATABASE math_tutor;
CREATE USER bot_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE math_tutor_bot TO bot_user;
\q
```

5. **Настройте .env** как описано выше

6. **Примените миграции:**
```bash
alembic upgrade head
```

7. **Создайте systemd сервис:**
```bash
sudo nano /etc/systemd/system/math-tutor-bot.service
```

```ini
[Unit]
Description=Math Tutor Telegram Bot
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/math-tutor-bot
Environment="PATH=/opt/math-tutor-bot/venv/bin"
ExecStart=/opt/math-tutor-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Запустите сервис:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable math-tutor-bot
sudo systemctl start math-tutor-bot
sudo systemctl status math-tutor-bot
```

9. **Просмотр логов:**
```bash
sudo journalctl -u math-tutor-bot -f
```

## 📈 Масштабирование

Для увеличения производительности:

1. **Настройте connection pool для PostgreSQL**

2. **Настройте connection pool для PostgreSQL**

3. **Используйте webhook вместо polling:**
   - Настройте nginx
   - Измените код в `main.py` для webhook

## 📄 Лицензия

Коммерческий проект. Все права защищены.

## 👨‍💻 Поддержка

При возникновении проблем создайте issue в репозитории проекта.

---

**Бот готов к использованию!** 🎉

Создавайте коды доступа и приглашайте пользователей!
