# Как добавлять новые материалы

Весь курс описывается в одном файле:

```text
content/chapters.json
```

Правила лежат общим списком в поле `rules`, а главы лежат в поле `chapters`.

## 1. Словарь главы

Создай файл:

```text
words/chapter5.json
```

Формат:

```json
[
  {
    "arabic": "كِتَاب",
    "translation": "книга"
  }
]
```

## 2. Диалоги главы

Положи картинки сюда:

```text
dialogues/chapter5/dialog1.png
dialogues/chapter5/dialog2.png
```

## 3. Новая глава в `content/chapters.json`

Добавь объект в массив `chapters`:

```json
{
  "id": "chapter5",
  "title": "Глава 5 — Название",
  "subtitle": "Короткое описание главы.",
  "words": "words/chapter5.json",
  "webWords": "data/chapter5.json",
  "dialogs": [
    {
      "title": "Диалог 1 — Название",
      "path": "dialogues/chapter5/dialog1.png",
      "webPath": "media/dialogues/chapter5/dialog1.png"
    }
  ]
}
```

## 4. Новое правило

Положи картинку в:

```text
rules/14.png
```

И добавь объект в массив `rules`:

```json
{
  "title": "Название правила",
  "tag": "Тема",
  "path": "rules/14.png",
  "webPath": "media/rules/14.png"
}
```

## 5. Обновить Web App

После добавления файлов запусти:

```powershell
py sync_webapp_content.py
```

Потом проверь локально:

```powershell
py serve_webapp.py
```

И открой:

```text
http://127.0.0.1:8080/webapp/index.html
```
