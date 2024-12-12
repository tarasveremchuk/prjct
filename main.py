import telebot
from telebot import types
import os
import random
import time

# Ініціалізація бота з токеном
TOKEN = "7917914353:AAHwAoyDh9PbRlayBedZnCvSQcP43NdL_qE"
bot = telebot.TeleBot(TOKEN)

ADMIN_USER_ID = 6151460786
GROUP_ID = "@darkbotgroup"
user_feedback_data = {}
last_file_time = {}
FILE_COOLDOWN = 14400  # 24 години в секундах

# Список статей для кнопок
articles = [
    "Рефаунд", "Арбитраж", "Документы", "Криптовалюта",
    "Трейдинг", "Инвестиции", "Мотивация", "Программирование",
    "Искусственный интеллект", "Маркетинг", "UI/UX", "Фриланс"
]

# Кількість кнопок на сторінку
BUTTONS_PER_PAGE = 4


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Створення клавіатури
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn_articles = types.KeyboardButton("\ud83d\udcda Статьи и ресурсы")

    btn_about = types.KeyboardButton("\u2139\ufe0f О боте")
    btn_feedback = types.KeyboardButton("\u2709\ufe0f Обратная связь")


    # Додавання кнопок до клавіатури
    keyboard.add(btn_articles)
    keyboard.add(btn_about)
    keyboard.add(btn_feedback)

    # Відправка привітання з клавіатурою
    bot.send_message(
        message.chat.id,
        """👋 Приветствую! Я бот *TrueDarkBot*, создан, чтобы помочь вам найти и получить доступ к самой полезной информации! Вот что я могу предложить:

🔍 *Информация о рефаунде* — полезные советы и материалы.
📜 *Фото документов* и шаблоны для вашего удобства.
📰 *Слитые статьи* и интересные материалы из открытых источников.
🤖 *Нейросети* — самые интересные и полезные.
🌐 *Сайты* для упрощения работы и повседневных задач.
💼 *Возможности заработка:* арбитраж, криптовалюта, и многое другое.

⚠️ *ВСЯ ИНФОРМАЦИЯ БЫЛА ВЗЯТА ИСКЛЮЧИТЕЛЬНО ИЗ ОТКРЫТЫХ ИСТОЧНИКОВ!*

Давайте начнем! 🚀""",parse_mode='Markdown',
        reply_markup=keyboard
    )


@bot.message_handler(func=lambda message: message.text == "📚 Статьи и ресурсы")
def send_articles(message, page=0):
    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE

    # Створення кнопок для статей
    inline_keyboard = types.InlineKeyboardMarkup()
    for article in articles[start_index:end_index]:
        inline_keyboard.add(types.InlineKeyboardButton(article, callback_data=f"article_{article}"))

    # Кнопки для навігації
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Влево", callback_data=f"prev_{page - 1}"))
    if end_index < len(articles):
        nav_buttons.append(types.InlineKeyboardButton("Вправо ➡️", callback_data=f"next_{page + 1}"))
    if nav_buttons:
        inline_keyboard.row(*nav_buttons)

    bot.send_message(message.chat.id, "Выберите статью:", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("prev_") or call.data.startswith("next_"))
def navigate_articles(call):
    page = int(call.data.split("_")[1])
    start_index = page * BUTTONS_PER_PAGE
    end_index = start_index + BUTTONS_PER_PAGE

    # Створення кнопок для статей
    inline_keyboard = types.InlineKeyboardMarkup()
    for article in articles[start_index:end_index]:
        inline_keyboard.add(types.InlineKeyboardButton(article, callback_data=f"article_{article}"))

    # Кнопки для навігації
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Влево", callback_data=f"prev_{page - 1}"))
    if end_index < len(articles):
        nav_buttons.append(types.InlineKeyboardButton("Вправо ➡️", callback_data=f"next_{page + 1}"))
    if nav_buttons:
        inline_keyboard.row(*nav_buttons)

    bot.edit_message_text(
        "Выберите статью:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=inline_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("article_"))
def show_article_details(call):
    article_name = call.data.split("_", 1)[1]
    if article_name == "Рефаунд":
        check_and_send_file(call.message.chat.id, "refund")
    elif article_name == "Документы":
        send_random_folder_images(call.message.chat.id, "passports")
    else:
        bot.send_message(call.message.chat.id, f"Вы выбрали статью: {article_name}")


@bot.message_handler(func=lambda message: message.text == "\u2709\ufe0f Обратная связь")
def feedback_request(message):
    bot.send_message(message.chat.id, "Введите свой вопрос для связи с вами:")
    bot.register_next_step_handler(message, send_feedback_to_admin)


def send_feedback_to_admin(message):
    user_feedback = message.text
    user_feedback_data[message.chat.id] = user_feedback

    # Створення кнопки для відповіді
    reply_keyboard = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton("Ответить", callback_data=f"reply_{message.chat.id}")
    reply_keyboard.add(reply_button)

    bot.send_message(ADMIN_USER_ID, f"Новый вопрос от пользователя {message.chat.id}:\n{user_feedback}",
                     reply_markup=reply_keyboard)
    bot.send_message(message.chat.id, "Ваш вопрос отправлен. Спасибо!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_button(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(call.message.chat.id, "Введите ваш ответ:")
    bot.register_next_step_handler(call.message, send_reply_to_user, user_id)


def send_reply_to_user(message, user_id):
    admin_reply = message.text
    bot.send_message(user_id, f"Ответ от администратора:\n{admin_reply}")
    bot.send_message(message.chat.id, "Ответ отправлен пользователю.")


def check_and_send_file(chat_id, folder_name):
    if not is_user_subscribed(chat_id):
        bot.send_message(chat_id, f"Чтобы получить доступ к файлам, подпишитесь на группу: {GROUP_ID}")
        return

    # Перевірка статусу адміністратора
    try:
        member_status = bot.get_chat_member(GROUP_ID, chat_id).status
        if member_status in ["administrator", "creator"]:
            is_admin = True
        else:
            is_admin = False
    except Exception as e:
        print(f"Error checking admin status: {e}")
        is_admin = False

    # Адміністратори обходять кулдаун
    if not is_admin:
        current_time = time.time()
        last_time = last_file_time.get(chat_id, 0)

        if current_time - last_time < FILE_COOLDOWN:
            remaining_time = FILE_COOLDOWN - (current_time - last_time)
            bot.send_message(chat_id, f"Вы можете получить следующий файл через {int(remaining_time // 60)} минут.")
            return

        last_file_time[chat_id] = current_time

    # Надсилання файлу
    folder_path = os.path.join(os.getcwd(), folder_name)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith(".pdf") or f.endswith(".docx")]
        if files:
            random_file = random.choice(files)
            with open(os.path.join(folder_path, random_file), "rb") as file:
                bot.send_document(chat_id, file)
        else:
            bot.send_message(chat_id, "Нет доступных файлов в папке.")
    else:
        bot.send_message(chat_id, "Папка с файлами не найдена.")



def is_user_subscribed(chat_id):
    try:
        member_status = bot.get_chat_member(GROUP_ID, chat_id).status
        return member_status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

def send_random_folder_images(chat_id, base_folder):
    if not is_user_subscribed(chat_id):
        bot.send_message(
            chat_id,
            "Вы не подписаны на нашу группу! Подпишитесь, чтобы получить доступ к фото. 🚀",
        )
        return

    base_path = os.path.join(os.getcwd(), base_folder)

    if os.path.exists(base_path) and os.path.isdir(base_path):
        # Список підпапок
        subfolders = [
            os.path.join(base_path, f)
            for f in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, f))
        ]

        # Список зображень у підпапках
        folder_images = []
        for folder in subfolders:
            images = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.endswith((".jpg", ".png", ".jpeg"))
            ]
            folder_images.extend(images)

        # Список зображень безпосередньо в основній папці
        base_images = [
            os.path.join(base_path, f)
            for f in os.listdir(base_path)
            if f.endswith((".jpg", ".png", ".jpeg"))
        ]

        # Об'єднуємо всі зображення і обираємо випадкове з рівними шансами
        all_images = folder_images + base_images
        if all_images:
            random_image = random.choice(all_images)
            with open(random_image, "rb") as img:
                bot.send_message(chat_id, "Вот, держи фото:")
                bot.send_photo(chat_id, img)
        else:
            bot.send_message(chat_id, "В папке нет изображений")
    else:
        bot.send_message(chat_id, "Папка с документами не найдена")


@bot.message_handler(func=lambda message: message.text == "ℹ️ О боте")
def send_articles(message):
    bot.send_message(
        message.chat.id,
        """
👋 Приветствую! Я бот *TrueDarkBot* — ваш гид в мире полезной информации, инструментов и возможностей. Моя миссия — предоставить доступ к данным, которые помогут вам расширить свои знания и горизонты. Давайте познакомимся поближе!

*Что я предлагаю?*

*🔍 Рефаунд*
Я предоставляю материалы, которые помогут разобраться в теме рефаунда:

    • Подробные статьи с объяснением основных понятий и процессов.
    • Базовая терминология, чтобы даже новички могли понять, о чем идет речь.
    • Подборка полезных сайтов и ресурсов, которые могут пригодиться.
    • Злитые таблицы с актуальной информацией о магазинах, политике возвратов и лайфхаках.
        
*📜 Документы*
В моем архиве собрано более 1000+ фотографий паспортов, включая:

    • Документы иностранцев.
    • Паспортные данные стран СНГ.
    • Это может быть полезно для анализа, обучения или ознакомления с различными форматами документов.

*📰 Слитые статьи*
Собрание уникальных материалов, которые открывают новые горизонты:

    • Увлекательные истории про заработок.
    • Подробности о различных методах скама (в образовательных целях).
    • Основы и примеры социальной инженерии, которые помогут лучше понять человеческое поведение.
    • Редкие данные, которые редко встречаются в открытом доступе.

*🤖 Нейросети и инструменты*
Я расскажу о самых интересных и полезных нейросетях:

    • Инструменты для работы с текстами, изображениями, данными.
    • Полезные сайты для повседневной жизни и автоматизации задач.
    • Лучшие платформы для развития навыков и творчества.

*💼 Возможности заработка*
Я помогаю ориентироваться в мире заработка:

    • Обзор популярных направлений, таких как арбитраж и криптовалюта.
    • Полезные гайды и ссылки, чтобы вы могли быстро начать.

*⚠️ ВСЯ ИНФОРМАЦИЯ БЫЛА ВЗЯТА ИСКЛЮЧИТЕЛЬНО ИЗ ОТКРЫТЫХ ИСТОЧНИКОВ!*
Моя цель — предоставить вам доступ к данным, которые находятся в свободном обращении, и вдохновить вас на развитие и изучение новых возможностей.

Готовы начать? 🚀
        """, parse_mode='Markdown'
    )
@bot.message_handler(content_types=['text', 'photo', 'sticker', 'animation', 'video', 'document', 'audio', 'voice', 'location', 'contact', 'poll', 'dice', 'game', 'venue', 'video_note'])
def handle_unknown_message(message):
    bot.send_message(
        message.chat.id,
        "УПС... Я о таком еще не знал, нужно поискать в интернете 🤔"
    )

# Запуск бота
bot.polling(none_stop=True)
