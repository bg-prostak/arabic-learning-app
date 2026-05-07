import telebot
from telebot import types
import json
import random
import os

# =====================================================
# TOKEN
# =====================================================

TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)

# =====================================================
# НАСТРОЙКИ
# =====================================================

WORDS_PER_PAGE = 10
WEB_APP_URL = os.getenv("WEB_APP_URL", "").strip()
CONTENT_PATH = os.getenv("CONTENT_PATH", "content/chapters.json")

# Последнее отправленное медиа-сообщение по чату,
# чтобы заменять его новым и не засорять переписку.
last_media_messages = {}

# Состояния повторения и тестов по чатам.
repeat_state = {}
test_state = {}

# =====================================================
# КОНТЕНТ
# =====================================================

def load_content():

    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


content = load_content()
chapters = {
    chapter["id"]: chapter
    for chapter in content["chapters"]
}
rules_catalog = content.get("rules", [])

# =====================================================
# ЗАГРУЗКА СЛОВ
# =====================================================

def load_words(chapter):

    path = chapters[chapter]["words"]

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_rules_markup():

    markup = types.InlineKeyboardMarkup()

    for rule in rules_catalog:

        button = types.InlineKeyboardButton(
            rule["title"],
            callback_data=f"rule|{rule['path']}"
        )

        markup.add(button)

    return markup


def replace_media_message(chat_id, path):

    previous_message_id = last_media_messages.get(chat_id)

    if previous_message_id:

        try:
            bot.delete_message(chat_id, previous_message_id)
        except Exception:
            pass

    with open(path, "rb") as photo:

        sent_message = bot.send_photo(chat_id, photo)

    last_media_messages[chat_id] = sent_message.message_id


def build_repetition_chapters_markup():

    markup = types.InlineKeyboardMarkup()

    for chapter_key, chapter in chapters.items():

        button = types.InlineKeyboardButton(
            f"🔁 {chapter['title']}",
            callback_data=f"repeat_menu|{chapter_key}"
        )

        markup.add(button)

    return markup


def send_repetition_mode_menu(chat_id, chapter_key, message_id):

    chapter = chapters[chapter_key]
    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🔁 Повторение слов",
            callback_data=f"repeat|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "📝 Тест на 10 слов",
            callback_data=f"test_start|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К главам",
            callback_data="back_repeat"
        )
    )

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"🔁 <b>{chapter['title']}</b>\n\nВыбери режим:",
        parse_mode="HTML",
        reply_markup=markup
    )

# =====================================================
# ГЛАВНОЕ МЕНЮ
# =====================================================

def main_menu():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if WEB_APP_URL:
        markup.add(
            types.KeyboardButton(
                "📱 Открыть приложение",
                web_app=types.WebAppInfo(WEB_APP_URL)
            )
        )
    else:
        markup.add("📱 Приложение")

    markup.add("📖 Диалоги", "📚 Словарь")
    markup.add("📝 Правила", "🔁 Повторение")

    return markup

# =====================================================
# START
# =====================================================

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(
        message.chat.id,
        "📚 Arabic Bot\n\nОткрой приложение, чтобы учиться в удобном интерфейсе.",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "📱 Приложение")
def web_app_help(message):

    bot.send_message(
        message.chat.id,
        (
            "📱 Мини-приложение уже добавлено в проект.\n\n"
            "Чтобы кнопка открывала его прямо в Telegram, запусти бота с переменной WEB_APP_URL, "
            "где указан HTTPS-адрес файла webapp/index.html."
        )
    )

# =====================================================
# ДИАЛОГИ
# =====================================================

@bot.message_handler(func=lambda m: m.text == "📖 Диалоги")
def dialogues(message):

    markup = types.InlineKeyboardMarkup()

    for chapter_key, chapter in chapters.items():

        button = types.InlineKeyboardButton(
            f"📖 {chapter['title']}",
            callback_data=f"dialogs|{chapter_key}"
        )

        markup.add(button)

    bot.send_message(
        message.chat.id,
        "📖 Выбери главу:",
        reply_markup=markup
    )

# =====================================================
# ПРАВИЛА
# =====================================================

@bot.message_handler(func=lambda m: m.text == "📝 Правила")
def rules(message):

    bot.send_message(
        message.chat.id,
        "📝 Выбери правило:",
        reply_markup=build_rules_markup()
    )

# =====================================================
# СЛОВАРЬ
# =====================================================

@bot.message_handler(func=lambda m: m.text == "📚 Словарь")
def vocabulary(message):

    markup = types.InlineKeyboardMarkup()

    for chapter_key, chapter in chapters.items():

        button = types.InlineKeyboardButton(
            f"📚 {chapter['title']}",
            callback_data=f"vocab|{chapter_key}|0"
        )

        markup.add(button)

    bot.send_message(
        message.chat.id,
        "📚 Выбери главу:",
        reply_markup=markup
    )

# =====================================================
# ПОВТОРЕНИЕ
# =====================================================

@bot.message_handler(func=lambda m: m.text == "🔁 Повторение")
def repetition(message):

    bot.send_message(
        message.chat.id,
        "🔁 Выбери главу:",
        reply_markup=build_repetition_chapters_markup()
    )

# =====================================================
# СТРАНИЦА СЛОВАРЯ
# =====================================================

def send_words_page(chat_id, chapter_key, page, message_id=None):

    words = load_words(chapter_key)

    chapter_title = chapters[chapter_key]["title"]

    total_pages = (len(words) - 1) // WORDS_PER_PAGE + 1

    start = page * WORDS_PER_PAGE
    end = start + WORDS_PER_PAGE

    current_words = words[start:end]

    text = (
        f"📘 <b>{chapter_title}</b>\n"
        f""
        f"📄 Страница {page + 1} / {total_pages}\n\n"
    )

    for word in current_words:

        text += (
            f"🔹 <b>{word['arabic']}</b>\n"
            f"{word['translation']}\n\n"
        )

    markup = types.InlineKeyboardMarkup()

    buttons = []

    if page > 0:

        prev_button = types.InlineKeyboardButton(
            "⬅ Назад",
            callback_data=f"vocab|{chapter_key}|{page - 1}"
        )

        buttons.append(prev_button)

    if page < total_pages - 1:

        next_button = types.InlineKeyboardButton(
            "➡ Далее",
            callback_data=f"vocab|{chapter_key}|{page + 1}"
        )

        buttons.append(next_button)

    if buttons:
        markup.row(*buttons)

    # Кнопка назад к главам
    markup.add(
        types.InlineKeyboardButton(
            "📚 К главам",
            callback_data="back_vocab"
        )
    )

    # EDIT MESSAGE
    if message_id:

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )

    else:

        bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=markup
        )

# =====================================================
# СЛУЧАЙНОЕ СЛОВО
# =====================================================

def send_random_word(chat_id, chapter_key, message_id=None):

    words = load_words(chapter_key)

    word = random.choice(words)
    repeat_state[chat_id] = {
        "chapter_key": chapter_key,
        "word": word
    }

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "👁 Показать перевод",
            callback_data=f"show|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "➡ Следующее слово",
            callback_data=f"repeat|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К главам",
            callback_data="back_repeat"
        )
    )

    text = f"🔹 <b>{word['arabic']}</b>"

    # EDIT MESSAGE
    if message_id:

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=markup
        )

    else:

        bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=markup
        )


def start_test(chat_id, chapter_key, message_id):

    words = load_words(chapter_key)
    question_count = min(10, len(words))
    questions = random.sample(words, question_count)

    test_state[chat_id] = {
        "chapter_key": chapter_key,
        "questions": questions,
        "current_index": 0,
        "score": 0
    }

    send_test_question(chat_id, message_id)


def send_test_question(chat_id, message_id):

    state = test_state[chat_id]
    chapter_key = state["chapter_key"]
    questions = state["questions"]
    current_index = state["current_index"]
    current_word = questions[current_index]
    all_words = load_words(chapter_key)

    wrong_translations = [
        word["translation"]
        for word in all_words
        if word["translation"] != current_word["translation"]
    ]

    option_count = min(3, len(wrong_translations))
    options = random.sample(wrong_translations, option_count)
    options.append(current_word["translation"])
    random.shuffle(options)

    state["correct_option"] = options.index(current_word["translation"])

    markup = types.InlineKeyboardMarkup()

    for index, option in enumerate(options):
        markup.add(
            types.InlineKeyboardButton(
                option,
                callback_data=f"test_answer|{index}"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К главам",
            callback_data="back_repeat"
        )
    )

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            f"📝 <b>Тест</b>\n"
            f"Вопрос {current_index + 1} / {len(questions)}\n\n"
            f"Что значит:\n"
            f"🔹 <b>{current_word['arabic']}</b>"
        ),
        parse_mode="HTML",
        reply_markup=markup
    )


def send_test_result(chat_id, message_id, is_correct):

    state = test_state[chat_id]
    current_word = state["questions"][state["current_index"]]
    is_last_question = state["current_index"] == len(state["questions"]) - 1

    markup = types.InlineKeyboardMarkup()

    if is_last_question:
        markup.add(
            types.InlineKeyboardButton(
                "🏁 Показать результат",
                callback_data="test_finish"
            )
        )
    else:
        markup.add(
            types.InlineKeyboardButton(
                "➡ Следующий вопрос",
                callback_data="test_next"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К главам",
            callback_data="back_repeat"
        )
    )

    result_text = "✅ Верно!" if is_correct else "❌ Неверно!"

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            f"{result_text}\n\n"
            f"🔹 <b>{current_word['arabic']}</b>\n"
            f"📖 {current_word['translation']}\n\n"
            f"Баллы: {state['score']} / {len(state['questions'])}"
        ),
        parse_mode="HTML",
        reply_markup=markup
    )


def finish_test(chat_id, message_id):

    state = test_state.get(chat_id)

    if not state:
        return

    score = state["score"]
    total = len(state["questions"])
    chapter_key = state["chapter_key"]
    chapter = chapters[chapter_key]

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🔁 Пройти ещё раз",
            callback_data=f"test_start|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К режимам",
            callback_data=f"repeat_menu|{chapter_key}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "🔁 К главам",
            callback_data="back_repeat"
        )
    )

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            f"🏁 <b>Тест завершён</b>\n\n"
            f"{chapter['title']}\n"
            f"Результат: <b>{score} / {total}</b>"
        ),
        parse_mode="HTML",
        reply_markup=markup
    )

# =====================================================
# CALLBACKS
# =====================================================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    data = call.data.split("|")

    action = data[0]

    # =================================================
    # ДИАЛОГИ
    # =================================================

    if action == "dialogs":

        chapter_key = data[1]

        chapter = chapters[chapter_key]

        markup = types.InlineKeyboardMarkup()

        for dialog in chapter.get("dialogs", []):

            button = types.InlineKeyboardButton(
                dialog["title"],
                callback_data=f"dialog_photo|{dialog['path']}"
            )

            markup.add(button)

        markup.add(
            types.InlineKeyboardButton(
                "📖 К главам",
                callback_data="back_dialogs"
            )
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📖 <b>{chapter['title']}</b>\n\nВыбери диалог:",
            parse_mode="HTML",
            reply_markup=markup
        )

    # =================================================
    # ФОТО ДИАЛОГА
    # =================================================

    elif action == "dialog_photo":

        path = data[1]

        if os.path.exists(path):
            replace_media_message(call.message.chat.id, path)

    # =================================================
    # ПРАВИЛА
    # =================================================

    elif action == "rule":

        path = data[1]

        if os.path.exists(path):
            replace_media_message(call.message.chat.id, path)

    # =================================================
    # СЛОВАРЬ
    # =================================================

    elif action == "vocab":

        chapter_key = data[1]
        page = int(data[2])

        send_words_page(
            chat_id=call.message.chat.id,
            chapter_key=chapter_key,
            page=page,
            message_id=call.message.message_id
        )

    # =================================================
    # МЕНЮ РЕЖИМОВ ПОВТОРЕНИЯ
    # =================================================

    elif action == "repeat_menu":

        chapter_key = data[1]

        send_repetition_mode_menu(
            chat_id=call.message.chat.id,
            chapter_key=chapter_key,
            message_id=call.message.message_id
        )

    # =================================================
    # НАЗАД К ГЛАВАМ СЛОВАРЯ
    # =================================================

    elif action == "back_vocab":

        markup = types.InlineKeyboardMarkup()

        for chapter_key, chapter in chapters.items():

            button = types.InlineKeyboardButton(
                f"📚 {chapter['title']}",
                callback_data=f"vocab|{chapter_key}|0"
            )

            markup.add(button)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📚 Выбери главу:",
            reply_markup=markup
        )

    # =================================================
    # НАЗАД К ГЛАВАМ ПРАВИЛ
    # =================================================

    elif action == "back_rules":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📝 Выбери правило:",
            reply_markup=build_rules_markup()
        )

    # =================================================
    # ПОВТОРЕНИЕ
    # =================================================

    elif action == "repeat":

        chapter_key = data[1]

        send_random_word(
            chat_id=call.message.chat.id,
            chapter_key=chapter_key,
            message_id=call.message.message_id
        )

    # =================================================
    # ПОКАЗАТЬ ПЕРЕВОД
    # =================================================

    elif action == "show":

        chapter_key = data[1]
        state = repeat_state.get(call.message.chat.id)

        if not state or state["chapter_key"] != chapter_key:
            send_random_word(
                chat_id=call.message.chat.id,
                chapter_key=chapter_key,
                message_id=call.message.message_id
            )
            return

        word = state["word"]

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "➡ Следующее слово",
                callback_data=f"repeat|{chapter_key}"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "🔁 К главам",
                callback_data="back_repeat"
            )
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📖 {word['translation']}",
            parse_mode="HTML",
            reply_markup=markup
        )

    # =================================================
    # СТАРТ ТЕСТА
    # =================================================

    elif action == "test_start":

        chapter_key = data[1]

        start_test(
            chat_id=call.message.chat.id,
            chapter_key=chapter_key,
            message_id=call.message.message_id
        )

    # =================================================
    # ОТВЕТ В ТЕСТЕ
    # =================================================

    elif action == "test_answer":

        state = test_state.get(call.message.chat.id)

        if not state:
            return

        selected_option = int(data[1])
        is_correct = selected_option == state["correct_option"]

        if is_correct:
            state["score"] += 1

        send_test_result(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            is_correct=is_correct
        )

    # =================================================
    # СЛЕДУЮЩИЙ ВОПРОС ТЕСТА
    # =================================================

    elif action == "test_next":

        state = test_state.get(call.message.chat.id)

        if not state:
            return

        state["current_index"] += 1

        send_test_question(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

    # =================================================
    # ЗАВЕРШЕНИЕ ТЕСТА
    # =================================================

    elif action == "test_finish":

        finish_test(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

    # =================================================
    # НАЗАД К ГЛАВАМ ПОВТОРЕНИЯ
    # =================================================

    elif action == "back_repeat":
        repeat_state.pop(call.message.chat.id, None)
        test_state.pop(call.message.chat.id, None)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔁 Выбери главу:",
            reply_markup=build_repetition_chapters_markup()
        )

    # =================================================
    # НАЗАД К ГЛАВАМ ДИАЛОГОВ
    # =================================================

    elif action == "back_dialogs":

        markup = types.InlineKeyboardMarkup()

        for chapter_key, chapter in chapters.items():

            button = types.InlineKeyboardButton(
                f"📖 {chapter['title']}",
                callback_data=f"dialogs|{chapter_key}"
            )

            markup.add(button)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📖 Выбери главу:",
            reply_markup=markup
        )

# =====================================================
# ЗАПУСК
# =====================================================

print("Бот запущен...")

bot.infinity_polling()
