import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get("BOT_TOKEN", "8635822480:AAFmiNT9AKM1GQa9ySK9i_mvBNMNZeZ_WGQ")
ADMIN_ID = 578606753
WEB_APP_URL = "https://t.me/IT_krgutis_bot/IT_rgutis"

# ========== СОСТОЯНИЯ FSM ==========
class QuizStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()

class FeedbackState(StatesGroup):
    waiting_question = State()

class RegisterState(StatesGroup):
    waiting_name = State()
    waiting_phone = State()

# ========== INLINE КЛАВИАТУРЫ ==========
GAME_INLINE_KB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎮 Открыть IT Мастерскую", url=WEB_APP_URL)]
])

def quiz_kb(options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=data)]
        for text, data in options
    ])

CANCEL_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

# ========== ТЕКСТЫ ==========
TEXTS = {
    "start": (
        "🤖 Добро пожаловать в IT-Мастерскую РГУТИС!\n\n"
        "Я помогу вам узнать о колледже, IT-специальностях, днях открытых дверей и не только.\n\n"
        "👇 Выберите нужный раздел:"
    ),
    "college": (
        "🏛️ Колледж РГУТИС\n\n"
        "📍 Адрес: Московская область, д.п. Черкизово, ул. Главная 100\n\n"
        "📞 Телефон: +7 (495) 940-83-58\n\n"
        "📧 Email: k-rgutis@bk.ru\n\n"
        "🌐 Сайт: rgutis.ru\n\n"
        "Почему выбирают нас:\n"
        "✅ Современные лаборатории\n"
        "✅ Преподаватели-практики\n"
        "✅ Стажировки в IT-компаниях\n"
        "✅ Трудоустройство после выпуска"
    ),
    "specialnosti": (
        "💻 IT-специальности РГУТИС\n\n"
        "1️⃣ 09.02.07 Информационные системы и программирование (набор закрыт)\n"
        "🎓 Программист\n"
        "📚 3 г 10 мес\n"
        "💰 140 000 ₽ в год\n\n"
        "2️⃣ 09.02.07 Веб-разработка (с 2027 г)\n\n"
        "🎓 Разработчик веб-приложений\n"
        "📚 2 г 10 мес\n"
        "💰 145 300 ₽ в год\n"
        "🗳️ 0 бюджетных мест\n\n"
        "3️⃣ 09.02.11  Разработка и управление программным обеспечением\n\n"
        "🎓 Программист\n"
        "📚 3 г 10 мес\n"
        "💰 145 300 ₽ в год\n"
        "🗳️ 12 бюджетных мест\n\n"
        "4️⃣ 09.02.12 Техническая эксплуатация и сопровождение информационных систем\n\n"
        "🎓 Специалист по технической эксплуатации и сопровождению информационных систем (СисАдмин)\n\n"
        "📚 3 г 10 мес\n"
        "💰 145 300 ₽ в год\n"
        "🗳️ 13 бюджетных мест"
    ),
    "messenger": (
        "📸 Подписывайся на наши соц сети, будь в курсе событий\n\n"
        "Мы в VK: https://vk.ru/rgutiscollege\n"
        "Мы в Telegram : https://t.me/krgutis\n"
        "Мы в Max: https://max.ru/join/jZW5HwocV_htKa9J56NCR2LRazJ4Omda0csat_p6ugI\n\n"
        "Игра: t.me/IT_krgutis_bot/IT_rgutis"
    ),
    "contacts": (
        "🏛️ Колледж РГУТИС\n\n"
        "📍 Адрес: Московская область, д.п. Черкизово, ул. Главная 100\n\n"
        "🕐 Режим работы:\n"
        "пн-чт: с 09:00 до 18:00\n"
        "пт: с 09:00 до 16:45\n"
        "с 13:00 до 14:00 — обед\n"
        "сб-вс — выходной\n\n"
        "📞 Телефоны:\n"
        "8-(800)-301-44-55\n"
        "+7 (495) 940-83-58\n"
        "+7 (977) 335-55-38\n"
        "+7 (495) 940-83-57\n\n"
        "📧 Email:\n"
        "priem@tgutis.ru\n"
        "info@rguts.ru\n"
        "k-rgutis@bk.ru\n\n"
        "🌐 Сайт: rgutis.ru\n\n"
        "VK: https://vk.com/rgutiscollege\n"
        "Telegram: https://t.me/krgutis\n"
        "Max: https://max.ru/join/jZW5HwocV_htKa9J56NCR2LRazJ4Omda0csat_p6ugI"
    ),
    "openday": (
        "📅 День открытых дверей в РГУТИС\n\n"
        "Приглашаем будущих абитуриентов и их родителей 28 марта 2026 года.\n\n"
        "Программа:\n"
        "• Общение с преподавателями\n"
        "• Актуальные данные о приёме на 2026 год\n"
        "• Увлекательный квест от высших школ университета\n\n"
        "📍 Место: Московская область, Пушкинский г.о., Черкизово, ул. Главная, д. 99\n\n"
        "🕚 Время: 11:00\n\n"
        "С нетерпением ждём встречи с вами в РГУТИС!"
    ),
    "faq": (
        "❓ Часто задаваемые вопросы\n\n"
        "📌 Какие документы нужны для поступления?\n"
        "→ Используйте команду /docs или кнопку «Документы»\n\n"
        "📌 Есть ли общежитие?\n"
        "→ Да, общежитие предоставляется иногородним студентам.\n\n"
        "📌 Можно ли поступить на бюджет?\n"
        "→ Да! По специальностям 09.02.11 — 12 мест, 09.02.12 — 13 мест.\n\n"
        "📌 После колледжа можно поступить в вуз?\n"
        "→ Да, выпускники могут поступить в РГУТИС или другой вуз по сокращённой программе.\n\n"
        "📌 Есть ли практика?\n"
        "→ Да, практика организована в IT-компаниях-партнёрах.\n\n"
        "📌 Как записаться на день открытых дверей?\n"
        "→ Нажмите «📝 Записаться на ДОД» в меню.\n\n"
        "📌 Остались вопросы?\n"
        "→ Нажмите «💬 Задать вопрос» и мы ответим!"
    ),
    "docs": (
        "📄 Документы для поступления\n\n"
        "Для граждан РФ:\n"
        "✅ Паспорт (оригинал + копия)\n"
        "✅ Аттестат об окончании 9 или 11 класса (оригинал + копия)\n"
        "✅ Фотографии 3×4 — 4 шт.\n"
        "✅ СНИЛС (копия)\n"
        "✅ Медицинская справка форма 086/у\n"
        "✅ Прививочный сертификат\n\n"
        "Дополнительно:\n"
        "📋 Заявление о приёме (заполняется на месте)\n"
        "📋 Согласие на обработку персональных данных\n\n"
        "При наличии льгот:\n"
        "📋 Справка об инвалидности\n"
        "📋 Документы, подтверждающие льготы\n\n"
        "📞 По вопросам приёма: +7 (495) 940-83-58\n"
        "📧 priem@tgutis.ru"
    ),
    "schedule": (
        "📅 Расписание дней открытых дверей 2026\n\n"
        "🗓️ 28 марта 2026 — Весенний день открытых дверей\n"
        "🕚 11:00 | Черкизово, ул. Главная, д. 99\n\n"
        "Следите за анонсами в наших соцсетях:\n"
        "Telegram: https://t.me/krgutis\n"
        "VK: https://vk.ru/rgutiscollege"
    ),
    "news": (
        "📰 Новости колледжа РГУТИС\n\n"
        "🔹 Март 2026\n"
        "День открытых дверей состоится 28 марта! Приходите и узнайте всё об IT-специальностях.\n\n"
        "🔹 Февраль 2026\n"
        "Студенты колледжа победили в региональном хакатоне по веб-разработке.\n\n"
        "🔹 Январь 2026\n"
        "Открыт приём документов на специальности 09.02.11 и 09.02.12 на 2026/2027 учебный год.\n\n"
        "Все новости — в нашем Telegram: https://t.me/krgutis"
    ),
}

# ========== РЕЗУЛЬТАТЫ КВИЗА ==========
QUIZ_RESULTS = {
    "A": (
        "💻 Тебе подходит: 09.02.11 Разработка и управление программным обеспечением\n\n"
        "Ты любишь писать код и разбираться в алгоритмах. Эта специальность для тебя!\n"
        "🎓 Квалификация: Программист\n"
        "📚 Срок: 3 г 10 мес | 💰 145 300 ₽/год | 🗳️ 12 бюджетных мест"
    ),
    "B": (
        "🖥️ Тебе подходит: 09.02.12 Техническая эксплуатация и сопровождение ИС\n\n"
        "Ты любишь работать с железом, сетями и решать технические задачи. Это твоё!\n"
        "🎓 Квалификация: Системный администратор\n"
        "📚 Срок: 3 г 10 мес | 💰 145 300 ₽/год | 🗳️ 13 бюджетных мест"
    ),
    "C": (
        "🌐 Тебе подходит: 09.02.07 Веб-разработка (с 2027 г)\n\n"
        "Тебе нравится создавать красивые и удобные сайты. Тогда вперёд в веб!\n"
        "🎓 Квалификация: Разработчик веб-приложений\n"
        "📚 Срок: 2 г 10 мес | 💰 145 300 ₽/год"
    ),
    "D": (
        "🔧 Тебе подходит: 09.02.11 Разработка и управление программным обеспечением\n\n"
        "Ты хочешь управлять разработкой и создавать качественные продукты в команде.\n"
        "🎓 Квалификация: Программист\n"
        "📚 Срок: 3 г 10 мес | 💰 145 300 ₽/год | 🗳️ 12 бюджетных мест"
    ),
}

# ========== ВОПРОСЫ КВИЗА ==========
QUIZ_QUESTIONS = [
    {
        "text": "🎯 Вопрос 1 из 5\n\nЧто тебе нравится больше всего?",
        "options": [
            ("💻 Писать программы и код", "A"),
            ("🔧 Настраивать компьютеры и сети", "B"),
            ("🎨 Создавать сайты и интерфейсы", "C"),
            ("📋 Планировать и управлять проектами", "D"),
        ]
    },
    {
        "text": "🎯 Вопрос 2 из 5\n\nКакой стиль работы тебе ближе?",
        "options": [
            ("💡 Работа за кодом в одиночку", "A"),
            ("🛠️ Работа с оборудованием", "B"),
            ("🖌️ Визуальное оформление", "C"),
            ("🤝 Координация команды", "D"),
        ]
    },
    {
        "text": "🎯 Вопрос 3 из 5\n\nЧто тебе интереснее изучать?",
        "options": [
            ("🔢 Алгоритмы и структуры данных", "A"),
            ("🌐 Сети и администрирование", "B"),
            ("📱 HTML, CSS, JavaScript", "C"),
            ("📊 Методологии разработки ПО", "D"),
        ]
    },
    {
        "text": "🎯 Вопрос 4 из 5\n\nКакой продукт ты хочешь создавать?",
        "options": [
            ("📱 Приложения и программы", "A"),
            ("🏗️ Надёжные IT-инфраструктуры", "B"),
            ("🌍 Красивые и удобные сайты", "C"),
            ("✅ Качественное ПО в команде", "D"),
        ]
    },
    {
        "text": "🎯 Вопрос 5 из 5\n\nТы предпочитаешь...",
        "options": [
            ("🧠 Разрабатывать алгоритмы", "A"),
            ("⚙️ Решать технические проблемы", "B"),
            ("🎭 Работать с дизайном и frontend", "C"),
            ("📈 Координировать разработку", "D"),
        ]
    },
]

# ========== ГЛАВНАЯ КЛАВИАТУРА ==========
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="🎓 О колледже"), KeyboardButton(text="💻 Специальности")],
        [KeyboardButton(text="📄 Документы"), KeyboardButton(text="❓ FAQ")],
        [KeyboardButton(text="📸 Соцсети"), KeyboardButton(text="📞 Контакты")],
        [KeyboardButton(text="📅 Дни открытых дверей"), KeyboardButton(text="📰 Новости")],
        [KeyboardButton(text="🎮 IT Мастерская")],
        [KeyboardButton(text="📝 Записаться на ДОД"), KeyboardButton(text="💬 Задать вопрос")],
        [KeyboardButton(text="🎲 Тест: какая специальность мне подходит?")],
        [KeyboardButton(text="🆘 Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ========== БОТ ==========
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ── /start ──────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXTS["start"], reply_markup=get_main_keyboard())

# ── /game ───────────────────────────────────────────────
@dp.message(Command("game"))
async def cmd_game(message: types.Message):
    await message.answer("🎮 IT Мастерская\nНажми на кнопку, чтобы открыть игру!", reply_markup=GAME_INLINE_KB)

# ── /college ────────────────────────────────────────────
@dp.message(Command("college"))
async def cmd_college(message: types.Message):
    await message.answer(TEXTS["college"])

# ── /specialnosti ───────────────────────────────────────
@dp.message(Command("specialnosti"))
async def cmd_specialnosti(message: types.Message):
    await message.answer(TEXTS["specialnosti"])

# ── /messenger ──────────────────────────────────────────
@dp.message(Command("messenger"))
async def cmd_messenger(message: types.Message):
    await message.answer(TEXTS["messenger"])

# ── /contacts ───────────────────────────────────────────
@dp.message(Command("contacts"))
async def cmd_contacts(message: types.Message):
    await message.answer(TEXTS["contacts"])

# ── /openday ────────────────────────────────────────────
@dp.message(Command("openday"))
async def cmd_openday(message: types.Message):
    await message.answer(TEXTS["openday"])

# ── /faq ────────────────────────────────────────────────
@dp.message(Command("faq"))
async def cmd_faq(message: types.Message):
    await message.answer(TEXTS["faq"])

# ── /docs ───────────────────────────────────────────────
@dp.message(Command("docs"))
async def cmd_docs(message: types.Message):
    await message.answer(TEXTS["docs"])

# ── /schedule ───────────────────────────────────────────
@dp.message(Command("schedule"))
async def cmd_schedule(message: types.Message):
    await message.answer(TEXTS["schedule"])

# ── /news ───────────────────────────────────────────────
@dp.message(Command("news"))
async def cmd_news(message: types.Message):
    await message.answer(TEXTS["news"])

# ── /help ───────────────────────────────────────────────
@dp.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🆘 Помощь\n\n"
        "Доступные команды:\n"
        "/start — Главное меню\n"
        "/college — О колледже\n"
        "/specialnosti — IT-специальности\n"
        "/docs — Документы для поступления\n"
        "/faq — Частые вопросы\n"
        "/schedule — Расписание дней открытых дверей\n"
        "/news — Новости\n"
        "/register — Записаться на день открытых дверей\n"
        "/ask — Задать вопрос\n"
        "/quiz — Тест: какая специальность подходит\n"
        "/game — IT Мастерская\n"
        "/messenger — Наши соцсети\n"
        "/contacts — Контакты\n"
        "/openday — День открытых дверей\n"
        "/help — Помощь",
        reply_markup=get_main_keyboard()
    )

# ══════════════════════════════════════════════════════════
# КВИЗ: какая специальность подходит
# ══════════════════════════════════════════════════════════
async def send_quiz_question(message: types.Message, index: int):
    q = QUIZ_QUESTIONS[index]
    kb = quiz_kb([(text, f"quiz_{data}") for text, data in q["options"]])
    await message.answer(q["text"], reply_markup=kb)

@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(QuizStates.q1)
    await state.update_data(answers=[])
    await message.answer(
        "🎲 Тест: какая IT-специальность тебе подходит?\n\n"
        "Отвечай честно — выбирай тот вариант, который ближе всего!",
        reply_markup=ReplyKeyboardRemove()
    )
    await send_quiz_question(message, 0)

@dp.message(F.text == "🎲 Тест: какая специальность мне подходит?")
async def btn_quiz(message: types.Message, state: FSMContext):
    await cmd_quiz(message, state)

async def process_quiz_answer(callback: types.CallbackQuery, state: FSMContext, next_state, q_index: int):
    answer = callback.data.replace("quiz_", "")
    data = await state.get_data()
    answers = data.get("answers", [])
    answers.append(answer)
    await state.update_data(answers=answers)
    await callback.answer()

    if q_index < len(QUIZ_QUESTIONS):
        await state.set_state(next_state)
        await send_quiz_question(callback.message, q_index)
    else:
        # Подсчёт результата
        from collections import Counter
        count = Counter(answers)
        result_key = count.most_common(1)[0][0]
        await state.clear()
        result_text = QUIZ_RESULTS.get(result_key, "Все специальности вам подходят!")
        await callback.message.answer(
            "🎉 Результат теста!\n\n" + result_text +
            "\n\nХотите записаться на день открытых дверей? Нажмите «📝 Записаться на ДОД»",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query(QuizStates.q1, F.data.startswith("quiz_"))
async def quiz_q1(callback: types.CallbackQuery, state: FSMContext):
    await process_quiz_answer(callback, state, QuizStates.q2, 1)

@dp.callback_query(QuizStates.q2, F.data.startswith("quiz_"))
async def quiz_q2(callback: types.CallbackQuery, state: FSMContext):
    await process_quiz_answer(callback, state, QuizStates.q3, 2)

@dp.callback_query(QuizStates.q3, F.data.startswith("quiz_"))
async def quiz_q3(callback: types.CallbackQuery, state: FSMContext):
    await process_quiz_answer(callback, state, QuizStates.q4, 3)

@dp.callback_query(QuizStates.q4, F.data.startswith("quiz_"))
async def quiz_q4(callback: types.CallbackQuery, state: FSMContext):
    await process_quiz_answer(callback, state, QuizStates.q5, 4)

@dp.callback_query(QuizStates.q5, F.data.startswith("quiz_"))
async def quiz_q5(callback: types.CallbackQuery, state: FSMContext):
    await process_quiz_answer(callback, state, None, 5)

# ══════════════════════════════════════════════════════════
# ЗАДАТЬ ВОПРОС
# ══════════════════════════════════════════════════════════
@dp.message(Command("ask"))
async def cmd_ask(message: types.Message, state: FSMContext):
    await state.set_state(FeedbackState.waiting_question)
    await message.answer(
        "💬 Напишите ваш вопрос — мы ответим как можно скорее!\n\n"
        "Для отмены нажмите ❌ Отмена",
        reply_markup=CANCEL_KB
    )

@dp.message(F.text == "💬 Задать вопрос")
async def btn_ask(message: types.Message, state: FSMContext):
    await cmd_ask(message, state)

@dp.message(FeedbackState.waiting_question)
async def receive_question(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено. Возвращаемся в меню.", reply_markup=get_main_keyboard())
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"
    question_text = (
        f"💬 Новый вопрос от пользователя!\n\n"
        f"👤 {user.full_name} ({username})\n"
        f"🆔 ID: {user.id}\n\n"
        f"❓ Вопрос:\n{message.text}"
    )

    await state.clear()
    await message.answer(
        "✅ Ваш вопрос отправлен! Мы ответим в ближайшее время.\n\n"
        "📞 Также можно позвонить: +7 (495) 940-83-58",
        reply_markup=get_main_keyboard()
    )

    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, question_text)
        except Exception:
            pass

# ══════════════════════════════════════════════════════════
# ЗАПИСЬ НА ДЕНЬ ОТКРЫТЫХ ДВЕРЕЙ
# ══════════════════════════════════════════════════════════
@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    await state.set_state(RegisterState.waiting_name)
    await message.answer(
        "📝 Запись на день открытых дверей\n\n"
        "Ближайший ДОД: 28 марта 2026, 11:00\n"
        "📍 Черкизово, ул. Главная, д. 99\n\n"
        "Введите ваше имя и фамилию:",
        reply_markup=CANCEL_KB
    )

@dp.message(F.text == "📝 Записаться на ДОД")
async def btn_register(message: types.Message, state: FSMContext):
    await cmd_register(message, state)

@dp.message(RegisterState.waiting_name)
async def register_name(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено. Возвращаемся в меню.", reply_markup=get_main_keyboard())
        return

    await state.update_data(name=message.text)
    await state.set_state(RegisterState.waiting_phone)
    await message.answer("Введите ваш номер телефона для связи:")

@dp.message(RegisterState.waiting_phone)
async def register_phone(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено. Возвращаемся в меню.", reply_markup=get_main_keyboard())
        return

    data = await state.get_data()
    name = data.get("name", "—")
    phone = message.text
    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"

    registration_text = (
        f"📝 Новая заявка на ДОД!\n\n"
        f"👤 {user.full_name} ({username})\n"
        f"🆔 ID: {user.id}\n\n"
        f"📋 Имя: {name}\n"
        f"📞 Телефон: {phone}\n\n"
        f"📅 Мероприятие: День открытых дверей 28 марта 2026"
    )

    await state.clear()
    await message.answer(
        f"✅ Отлично, {name}! Вы записаны на день открытых дверей.\n\n"
        "📅 28 марта 2026, 11:00\n"
        "📍 Черкизово, ул. Главная, д. 99\n\n"
        "Ждём вас! Если планы изменятся — свяжитесь с нами:\n"
        "📞 +7 (495) 940-83-58",
        reply_markup=get_main_keyboard()
    )

    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, registration_text)
        except Exception:
            pass

# ══════════════════════════════════════════════════════════
# ОБРАБОТКА КНОПОК МЕНЮ
# ══════════════════════════════════════════════════════════
@dp.message()
async def handle_buttons(message: types.Message, state: FSMContext):
    text = message.text

    # Отмена в любом состоянии
    if text == "❌ Отмена":
        await state.clear()
        await message.answer("Возвращаемся в меню.", reply_markup=get_main_keyboard())
        return

    button_map = {
        "🎓 О колледже": TEXTS["college"],
        "💻 Специальности": TEXTS["specialnosti"],
        "📸 Соцсети": TEXTS["messenger"],
        "📞 Контакты": TEXTS["contacts"],
        "📅 Дни открытых дверей": TEXTS["openday"],
        "❓ FAQ": TEXTS["faq"],
        "📄 Документы": TEXTS["docs"],
        "📰 Новости": TEXTS["news"],
    }

    if text in button_map:
        await message.answer(button_map[text])
    elif text == "🎮 IT Мастерская":
        await message.answer("🎮 IT Мастерская\nНажми на кнопку, чтобы открыть игру!", reply_markup=GAME_INLINE_KB)
    elif text == "🆘 Помощь":
        await cmd_help(message, state)
    else:
        await message.answer(
            "Используйте кнопки меню или команды.\n/help — список команд",
            reply_markup=get_main_keyboard()
        )

# ══════════════════════════════════════════════════════════
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
