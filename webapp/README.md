# Arabic Academy Web App

Мини-приложение для Telegram Web App.

## Как добавлять главы

Основной файл структуры:

```text
content/chapters.json
```

В нём описываются главы, словарь, диалоги и правила. После добавления новых файлов запусти из корня проекта:

```powershell
py sync_webapp_content.py
```

Скрипт скопирует материалы в `webapp/data` и `webapp/media`, а также обновит:

```text
webapp/content/chapters.json
```

## Локальный просмотр

```powershell
py serve_webapp.py
```

После запуска открой:

```text
http://127.0.0.1:8080/webapp/index.html
```

Для Telegram нужна HTTPS-ссылка. Когда приложение будет выложено на хостинг, запусти бота с переменной:

```powershell
$env:WEB_APP_URL="https://your-domain.example/index.html"
py bot.py
```

После этого в главном меню появится кнопка `📱 Открыть приложение`.
