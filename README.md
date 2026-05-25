# ByMeVPN Support Bot

Минималистичный support-бот на **aiogram 3** + **SQLAlchemy (aiosqlite)**.

## Структура

```
.
├── main.py                  # Точка входа
├── config.py                # Загрузка .env
├── states.py                # FSM-состояния
├── database/
│   ├── models.py            # ORM-модели (User, Ticket, Message)
│   └── repository.py        # Все операции с БД
├── handlers/
│   ├── common.py            # /start
│   ├── user.py              # Пользовательский сценарий
│   ├── admin.py             # Панель администратора
│   └── utils.py             # Вспомогательные функции
├── keyboards/
│   ├── user_kb.py           # Reply + Inline клавиатуры для пользователей
│   └── admin_kb.py          # Inline клавиатуры для администраторов
└── middlewares/
    └── ban_check.py         # Блокировка забаненных пользователей
```

## Запуск

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Заполнить .env
cp .env.example .env
# Вписать BOT_TOKEN и ADMIN_IDS

# 3. Запустить
python main.py
```

## Логика

| Действие | Описание |
|---|---|
| `📝 Написать запрос` | Создаёт новый тикет, уведомляет всех админов |
| `➕ Добавить в запрос` | Inline-кнопка — дослать файл/текст в тот же тикет |
| `✍️ Ответить` | Inline-кнопка — пользователь отвечает на ответ поддержки |
| `✉️ Ответить` | Inline-кнопка у админа — войти в режим ответа |
| `🚫 Заблокировать` | Inline-кнопка у админа — мгновенная блокировка |
| `/ban <id>` | Команда для блокировки по Telegram ID |
| `/unban <id>` | Команда для разблокировки по Telegram ID |
| `/help` | Список команд администратора |
