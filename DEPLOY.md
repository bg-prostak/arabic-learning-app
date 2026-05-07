# Деплой Arabic Bot

Проект состоит из двух частей:

- `webapp/` — Telegram Web App. Его публикуем на Vercel.
- `bot.py` — Telegram-бот. Его запускаем на Railway.

## 1. Важно про токен

Токен бота нельзя хранить в коде. Перед деплоем задай его через переменную окружения `BOT_TOKEN`.

Так как токен уже однажды был в коде, лучше перевыпустить его через BotFather:

```text
/revoke
```

Потом новый токен используй в Railway.

## 2. Деплой Web App на Vercel

Перед деплоем обнови материалы приложения:

```powershell
py sync_webapp_content.py
```

1. Создай аккаунт на Vercel.
2. Загрузи проект на GitHub.
3. В Vercel нажми `Add New Project`.
4. Выбери репозиторий.
5. В настройках проекта укажи:

```text
Root Directory: webapp
Framework Preset: Other
Build Command: оставить пустым
Output Directory: оставить пустым
Install Command: оставить пустым
```

6. Нажми `Deploy`.
7. После деплоя скопируй адрес приложения, например:

```text
https://arabic-bot.vercel.app
```

Итоговая ссылка для бота будет:

```text
https://arabic-bot.vercel.app/index.html
```

## 3. Деплой бота на Railway

1. Создай аккаунт на Railway.
2. Нажми `New Project`.
3. Выбери `Deploy from GitHub repo`.
4. Выбери этот же репозиторий.
5. В Variables добавь:

```text
BOT_TOKEN=твой_новый_токен_бота
WEB_APP_URL=https://arabic-bot.vercel.app/index.html
```

6. Railway сам установит зависимости из `requirements.txt`.
7. Команда запуска уже указана в `railway.json`:

```text
python bot.py
```

## 4. Проверка

1. Открой Telegram.
2. Зайди в своего бота.
3. Отправь `/start`.
4. Нажми `📱 Открыть приложение`.

Если открывается старый адрес, значит запущена старая версия бота или в Railway переменная `WEB_APP_URL` ещё не обновилась.
