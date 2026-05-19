# Как быстро добавлять новые материалы

Теперь не нужно вручную раскладывать файлы по `words`, `dialogues`, `webapp/data`, `webapp/media` и править несколько мест.

Есть один импортёр:

```text
import_content.py
```

Он сам:

- копирует словарь в `words`;
- копирует диалоги в `dialogues`;
- обновляет `content/chapters.json`;
- копирует всё в `webapp`;
- обновляет `webapp/content/chapters.json`.

## Добавить новую главу

1. Скопируй шаблон:

```text
content_inbox/chapter_template
```

Например, сделай папку:

```text
content_inbox/chapter6
```

2. Внутри должны лежать:

```text
chapter.json
words.json
dialog1.png
dialog2.png
dialog3.png
```

3. В `chapter.json` напиши название главы и диалогов:

```json
{
  "id": "chapter6",
  "title": "Глава 6 — Название главы",
  "subtitle": "Короткое описание главы.",
  "dialogs": [
    {
      "title": "Диалог 1 — Название",
      "file": "dialog1.png"
    }
  ]
}
```

4. В `words.json` добавь слова:

```json
[
  {
    "arabic": "كِتَاب",
    "translation": "книга"
  }
]
```

5. Запусти:

```powershell
py import_content.py chapter content_inbox/chapter6
```

Глава появится на сайте автоматически.

## Добавить новые правила

1. Скопируй шаблон:

```text
content_inbox/rules_template
```

Например:

```text
content_inbox/new_rules
```

2. Внутрь положи картинки:

```text
18.png
19.png
```

3. В `rules.json` опиши правила:

```json
{
  "rules": [
    {
      "title": "Название правила",
      "tag": "Правило",
      "file": "18.png"
    }
  ]
}
```

4. Запусти:

```powershell
py import_content.py rules content_inbox/new_rules
```

## Просто пересинхронизировать сайт

Если ты вручную поменял `content/chapters.json`, запусти:

```powershell
py import_content.py sync
```

## Проверить локально

```powershell
py serve_webapp.py
```

Открой:

```text
http://127.0.0.1:8080/webapp/index.html
```
