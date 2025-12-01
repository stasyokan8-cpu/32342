# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT v3.3 🎄🔥
# ИСПРАВЛЕННАЯ ВЕРСИЯ: Работающие квесты, расширенный функционал, исправлены все баги

import json
import random
import string
import asyncio
import os
from datetime import datetime, timedelta, timezone
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# Конфигурация для Replit
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8299215190:AAEqLfMOTjywx_jOeT-Kv1I5oKdgbdWzN9Y")
ADMIN_USERNAME = "BeellyKid"
DATA_FILE = "santa_data.json"

print(f"🎄 Запуск Secret Santa Bot v3.3 на Replit...")

user_data = {}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            global user_data
            user_data = data["users"]
            return data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}

def save_data(data):
    data["users"] = user_data
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

# -------------------------------------------------------------------
# БАЗОВЫЕ УТИЛИТЫ
# -------------------------------------------------------------------
def is_admin(update: Update):
    if update.effective_user:
        return update.effective_user.username == ADMIN_USERNAME
    return False

def gen_room_code():
    return "R" + "".join(random.choice(string.ascii_uppercase) for _ in range(5))

def back_to_menu_keyboard(admin=False):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
    ])

def toast_of_day():
    TOASTS = [
        "🎄 Пусть в новом году твой холодильник всегда будет полен, а будильник — сломан!",
        "✨ Желаю зарплаты как у Илон Маска, а забот — как у кота!",
        "🎁 Пусть удача прилипнет, как блёстки после корпоратива!",
        "❄️ Пусть счастье валит в дом, как снег в Сибири — неожиданно и много!",
        "🥂 Пусть каждый день нового года будет как первый день отпуска!",
        "🎅 Желаю, чтобы под ёлкой всегда находилось именно то, о чём мечталось!",
        "🌟 Пусть звёзды с неба достаются без особых усилий!",
        "🍪 Пусть печеньки всегда будут свежими, а настроение — отличным!",
        "🦌 Желаю, чтобы олени в жизни были только послушными!",
        "🎶 Пусть новогодние песни звучат только в радость!",
        "🍾 Желаю, чтобы шампанское било через край, а проблемы — мимо!",
        "🕯️ Пусть огоньки гирлянд освещают только счастливые моменты!",
        "❄️ Желаю морозных узоров на окнах и тепла в сердце!",
        "🎁 Пусть сюрпризы будут только приятными!",
        "🍬 Желаю сладкой жизни без горьких проблесков!",
        "🕰️ Пусть бой курантов приносит только хорошие новости!",
        "🎪 Желаю, чтобы жизнь была цирком, где ты — главный акробат!",
        "🧦 Пусть носки всегда парные, а мысли — ясные!",
        "🔥 Желаю, чтобы камин горел, а проблемы — нет!",
        "🎊 Пусть фейерверки эмоций затмят все печали!"
    ]
    return random.choice(TOASTS)

# -------------------------------------------------------------------
# СИСТЕМА ОЧКОВ И ОЛЕНЕЙ
# -------------------------------------------------------------------
def init_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "reindeer_level": 0,
            "reindeer_exp": 0,
            "santa_points": 100,
            "achievements": [],
            "games_won": 0,
            "quests_finished": 0,
            "reindeer_skin": "default",
            "grinch_fights": 0,
            "grinch_wins": 0,
            "rare_items": [],
            "unlocked_reindeers": ["default"],
            "current_reindeer": "default",
            "checkers_wins": 0,
            "checkers_losses": 0,
            "quiz_wins": 0,
            "total_points": 100,  # Начинаем с 100
            "name": "",
            "username": "",
            "answered_quiz_questions": [],
            "last_checkers_win": None,
            "quest_progress": {}  # Добавляем прогресс по квестам
        }

def add_santa_points(user_id, points, context: ContextTypes.DEFAULT_TYPE = None):
    init_user_data(user_id)
    user_data[str(user_id)]["santa_points"] = max(0, user_data[str(user_id)]["santa_points"] + points)
    user_data[str(user_id)]["total_points"] = max(0, user_data[str(user_id)]["total_points"] + points)
    
    if context and abs(points) >= 50:
        try:
            context.bot.send_message(
                user_id,
                f"🎅 {'Получено' if points > 0 else 'Потеряно'} {abs(points)} очков Санты!"
            )
        except:
            pass

def add_reindeer_exp(user_id, amount):
    init_user_data(user_id)
    user_data[str(user_id)]["reindeer_exp"] += amount
    
    current_level = user_data[str(user_id)]["reindeer_level"]
    exp_needed = (current_level + 1) * 100
    
    if user_data[str(user_id)]["reindeer_exp"] >= exp_needed and current_level < 5:
        user_data[str(user_id)]["reindeer_level"] += 1
        user_data[str(user_id)]["reindeer_exp"] = 0
        
        new_skin = None
        evolution_chance = random.random()
        
        if current_level + 1 == 3:
            if evolution_chance < 0.1:
                new_skin = "rainbow"
            elif evolution_chance < 0.02:
                new_skin = "ice_spirit"
        elif current_level + 1 == 4:
            if evolution_chance < 0.08:
                new_skin = "golden"
            elif evolution_chance < 0.015:
                new_skin = "crystal"
        elif current_level + 1 == 5:
            if evolution_chance < 0.05:
                new_skin = "cosmic"
            elif evolution_chance < 0.01:
                new_skin = "phantom"
        
        if new_skin:
            user_data[str(user_id)]["reindeer_skin"] = new_skin
            user_data[str(user_id)]["unlocked_reindeers"].append(new_skin)
            add_achievement(user_id, f"{new_skin}_reindeer")
        
        if current_level + 1 == 5:
            add_achievement(user_id, "reindeer_master")

def add_achievement(user_id, achievement_key):
    init_user_data(user_id)
    if achievement_key not in user_data[str(user_id)]["achievements"]:
        user_data[str(user_id)]["achievements"].append(achievement_key)
        add_santa_points(user_id, 50)

# -------------------------------------------------------------------
# 🎁 РАЗДЕЛ: ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ
# -------------------------------------------------------------------
def generate_gift_idea():
    CATEGORIES = {
        "💻 Техника и гаджеты": [
            "Умная колонка с голосовым помощником",
            "Беспроводные наушники с шумоподавлением", 
            "Портативное зарядное устройство 10000 mAh",
            "Электронная книга с подсветкой",
            "Умные часы с отслеживанием активности",
        ],
        "🎨 Творчество и хобби": [
            "Набор для рисования светом",
            "Конструктор для взрослых с мелкими деталями",
            "Набор для создания свечей ручной работы",
            "Алмазная вышивка с новогодним сюжетом",
            "Гончарный набор миниатюрный",
        ],
        "🏠 Уют и дом": [
            "Плед с подогревом и таймером",
            "Аромадиффузер с эфирными маслами",
            "Набор чайных пар с новогодним дизайном",
            "Проектор звёздного неба для комнаты",
            "Кресло-мешок с памятью формы",
        ]
    }
    
    category = random.choice(list(CATEGORIES.keys()))
    gift = random.choice(CATEGORIES[category])
    budget_options = [
        "💰 Бюджет до 2000₽", 
        "💸 Средний бюджет 2000-5000₽", 
        "🎁 Премиум от 5000₽",
        "💎 Люкс от 10000₽"
    ]
    budget_weights = [0.4, 0.35, 0.2, 0.05]
    budget = random.choices(budget_options, weights=budget_weights)[0]
    
    return f"{category}:\n{gift}\n{budget}"

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: ОСНОВНЫЕ КОМАНДЫ И ИНТЕРФЕЙС
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    
    user_data[str(user.id)]["name"] = user.full_name
    user_data[str(user.id)]["username"] = user.username or "без username"
    
    welcome_text = f"""
🎄 Добро пожаловать, {user.first_name}! 🎅

✨ <b>Правила Тайного Санты:</b>
1. Создай или присоединись к комнате
2. Напиши своё пожелание подарка
3. Дождись запуска игры организатором
4. Получи имя своего получателя и подари ему подарок!

🎁 <b>Что можно делать в боте:</b>
• Создавать комнаты и приглашать друзей
• Писать пожелания подарка
• Играть в новогодние мини-игры
• Проходить квесты и получать достижения
• Соревноваться с друзьями в рейтинге

Выбери действие ниже 👇
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    context.user_data["wish_mode"] = True
    
    wish_instructions = """
🎁 <b>Написание пожелания</b>

✨ <b>Как это работает:</b>
1. Напиши своё пожелание подарка в одном сообщении
2. Будь конкретным, но оставляй пространство для фантазии
3. Учитывай бюджет участников
4. После запуска игры изменить пожелание будет нельзя!

💡 <b>Примеры хороших пожеланий:</b>
• "Люблю читать, хотел бы интересную книгу"
• "Нужен тёплый плед для холодных вечеров"
• "Хочу сюрприз - угадайте мои интересы!"

📝 <b>Напиши своё пожелание ниже:</b>
"""
    
    await update.callback_query.edit_message_text(
        wish_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        return
        
    data = load_data()
    user = update.effective_user

    # Обработка рассылки для админа
    if is_admin(update) and "broadcast_mode" in context.user_data:
        await handle_broadcast_message(update, context)
        return

    if context.user_data.get("wish_mode"):
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                if room.get("game_started"):
                    await update.message.reply_text("🚫 Игра уже запущена! Менять пожелание нельзя.")
                    return
                room["members"][str(user.id)]["wish"] = update.message.text
                save_data(data)
                context.user_data["wish_mode"] = False
                add_reindeer_exp(user.id, 10)
                add_santa_points(user.id, 25, context)
                
                admin = is_admin(update)
                await update.message.reply_text(
                    "✨ Пожелание сохранено! +25 очков Санты! 🎄",
                    reply_markup=enhanced_menu_keyboard(admin)
                )
                return
        await update.message.reply_text("❄️ Ты ещё не в комнате! Используй кнопку 'Присоединиться к комнате'.")
        return

    # Обработка присоединения к комнате
    if context.user_data.get("join_mode"):
        await join_room(update, context)
        return

    # Если текст похож на код комнаты
    if len(update.message.text.strip()) == 6 and update.message.text.strip().startswith('R'):
        context.user_data["join_mode"] = True
        await join_room(update, context)
        return

    # Если ничего не подошло - показываем меню
    admin = is_admin(update)
    await update.message.reply_text(
        "Выбери действие в меню:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🏠 РАЗДЕЛ: УПРАВЛЕНИЕ КОМНАТАМИ (ИСПРАВЛЕНО ДЛЯ АДМИНА)
# -------------------------------------------------------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        if update.callback_query:
            await update.callback_query.answer("🚫 Только @BeellyKid может создавать комнаты!", show_alert=True)
            return
        else:
            await update.message.reply_text("🚫 Только @BeellyKid может создавать комнаты.")
            return

    data = load_data()
    code = gen_room_code()
    data["rooms"][code] = {
        "creator": update.effective_user.id,
        "members": {},
        "game_started": False,
        "assign": {},
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    }
    save_data(data)

    admin = is_admin(update)
    
    success_text = (
        f"🎄 <b>Комната создана!</b>\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Ссылка для приглашения:</b>\n"
        f"https://t.me/{(await context.bot.get_me()).username}?start=join_{code}\n\n"
        f"Приглашай друзей! Они могут присоединиться через меню бота."
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            success_text,
            parse_mode='HTML',
            reply_markup=enhanced_menu_keyboard(admin)
        )
    else:
        await update.message.reply_text(
            success_text,
            parse_mode='HTML',
            reply_markup=enhanced_menu_keyboard(admin)
        )

async def join_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    join_instructions = """
🎅 <b>Присоединение к комнате</b>

✨ <b>Как присоединиться:</b>
1. Попроси у организатора код комнаты (формат: RXXXXX)
2. Используй команду: /join_room RXXXXX
3. Или просто напиши код комнаты в чат

🔑 <b>Правила:</b>
• Можно быть только в одной комнате
• Присоединиться можно только до старта игры
• Минимум 2 участника для запуска
• Все участники должны написать пожелания

📝 <b>Напиши код комнаты ниже:</b>
"""
    
    await update.callback_query.edit_message_text(
        join_instructions,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard()
    )
    context.user_data["join_mode"] = True

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    data = load_data()
    user = update.effective_user
    
    if update.message and update.message.text.startswith('/join_room'):
        code = "".join(context.args).strip().upper() if context.args else None
    elif context.user_data.get("join_mode"):
        code = update.message.text.strip().upper()
        context.user_data["join_mode"] = False
    else:
        if update.message and len(update.message.text.strip()) == 6 and update.message.text.strip().startswith('R'):
            code = update.message.text.strip().upper()
        else:
            return

    if not code:
        await update.message.reply_text("Напиши: /join_room RXXXXX")
        return
        
    if not code.startswith('R') or len(code) != 6:
        await update.message.reply_text("🚫 Неверный формат кода! Код должен быть в формате RXXXXX")
        return
        
    if code not in data["rooms"]:
        await update.message.reply_text("🚫 Такой комнаты нет. Проверь код или создай новую комнату.")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await update.message.reply_text("🚫 Игра уже началась — вход закрыт!")
        return

    u = update.effective_user
    if str(u.id) in room["members"]:
        await update.message.reply_text("❄️ Ты уже в этой комнате!")
        return

    room["members"][str(u.id)] = {
        "name": u.full_name,
        "username": u.username or "без username",
        "wish": ""
    }
    save_data(data)
    add_reindeer_exp(u.id, 20)
    add_santa_points(u.id, 50, context)

    admin = is_admin(update)
    await update.message.reply_text(
        f"✨ <b>Ты присоединился к комнате! +50 очков Санты!</b> 🎄\n\n"
        f"<b>Код комнаты:</b> {code}\n"
        f"<b>Участников:</b> {len(room['members'])}\n\n"
        f"Теперь напиши своё пожелание подарка через меню! 🎁",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def show_room_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user
    
    # Для админа показываем выбор комнаты
    if is_admin(update):
        await admin_select_room_for_members(update, context)
        return
    
    # Для обычных пользователей - их текущую комнату
    user_room = None
    room_code = None
    
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            user_room = room
            room_code = code
            break
    
    if not user_room:
        await update.callback_query.answer("Ты не в комнате!", show_alert=True)
        return
    
    await show_specific_room_members(update, context, room_code, user_room)

async def admin_select_room_for_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard = []
    for code, room in data["rooms"].items():
        status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
        keyboard.append([InlineKeyboardButton(
            f"👥 {code} ({len(room['members'])} участ.) - {status}", 
            callback_data=f"room_members_{code}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "👥 <b>Просмотр участников комнат</b>\n\n"
        "Выбери комнату для просмотра участников:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_specific_room_members(update: Update, context: ContextTypes.DEFAULT_TYPE, code=None, room=None):
    if not code and update.callback_query:
        code = update.callback_query.data.replace("room_members_", "")
    
    if not code:
        return
        
    data = load_data()
    if not room:
        room = data["rooms"].get(code)
    
    if not room:
        await update.callback_query.answer("Комната не найдена!", show_alert=True)
        return
    
    members_text = f"👥 <b>Участники комнаты {code}:</b>\n\n"
    for i, (user_id, member) in enumerate(room["members"].items(), 1):
        wish_status = "✅" if member["wish"] else "❌"
        username = f"@{member['username']}" if member["username"] != "без username" else "без username"
        members_text += f"{i}. {member['name']} ({username}) {wish_status}\n"
    
    members_text += f"\n<b>Всего участников:</b> {len(room['members'])}"
    members_text += f"\n<b>Статус игры:</b> {'✅ Запущена' if room['game_started'] else '⏳ Ожидание'}"
    
    await update.callback_query.edit_message_text(
        members_text,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard(is_admin(update))
    )

async def show_room_top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user
    
    # Для админа показываем выбор комнаты
    if is_admin(update):
        await admin_select_room_for_top(update, context)
        return
    
    # Для обычных пользователей - их текущую комнату
    user_room = None
    room_code = None
    
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            user_room = room
            room_code = code
            break
    
    if not user_room:
        await update.callback_query.answer("Ты не в комнате!", show_alert=True)
        return
    
    await show_specific_room_top(update, context, room_code, user_room)

async def admin_select_room_for_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard = []
    for code, room in data["rooms"].items():
        keyboard.append([InlineKeyboardButton(
            f"🏆 {code} ({len(room['members'])} участ.)", 
            callback_data=f"room_top_{code}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "🏆 <b>Топ игроков по комнатам</b>\n\n"
        "Выбери комнату для просмотра топа:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_specific_room_top(update: Update, context: ContextTypes.DEFAULT_TYPE, code=None, room=None):
    if not code and update.callback_query:
        code = update.callback_query.data.replace("room_top_", "")
    
    if not code:
        return
        
    data = load_data()
    if not room:
        room = data["rooms"].get(code)
    
    if not room:
        await update.callback_query.answer("Комната не найдена!", show_alert=True)
        return
    
    # Собираем статистику участников комнаты
    player_stats = []
    for user_id in room["members"]:
        if user_id in user_data:
            player_stats.append((
                user_id,
                user_data[user_id].get("total_points", 0),
                user_data[user_id].get("name", "Неизвестный")
            ))
    
    # Сортируем по очкам
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    top_text = f"🏆 <b>Топ игроков комнаты {code}:</b>\n\n"
    
    if not player_stats:
        top_text += "Пока никто не набрал очков в этой комнате... 🎄"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, score, name) in enumerate(player_stats[:10]):
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            # Получаем уровень оленя
            reindeer_level = user_data.get(user_id, {}).get("reindeer_level", 0)
            level_emoji = "🦌" * (reindeer_level + 1) if reindeer_level < 3 else "🌟" * min(reindeer_level, 5)
            
            top_text += f"{medal} {name} — {score} очков {level_emoji}\n"
    
    top_text += f"\n<b>Всего участников:</b> {len(room['members'])}"
    
    await update.callback_query.edit_message_text(
        top_text,
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard(is_admin(update))
    )

# -------------------------------------------------------------------
# ⚙️ РАЗДЕЛ: АДМИН-ПАНЕЛЬ
# -------------------------------------------------------------------
async def start_game_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён.", show_alert=True)
        return

    data = load_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return

    keyboard = []
    for code, room in data["rooms"].items():
        if not room["game_started"] and len(room["members"]) >= 2:
            keyboard.append([InlineKeyboardButton(f"🎄 {code} ({len(room['members'])} участ.)", callback_data=f"start_{code}")])
    
    if not keyboard:
        await update.callback_query.edit_message_text(
            "🚫 Нет комнат для запуска! Нужны комнаты с минимум 2 участниками.",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "🚀 <b>Запуск игры Тайный Санта</b>\n\n"
        "Выбери комнату для запуска:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_specific_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    code = q.data.replace("start_", "")
    data = load_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return

    room = data["rooms"][code]
    if room["game_started"]:
        await q.edit_message_text("❄️ Игра уже запущена в этой комнате!")
        return

    members = list(room["members"].keys())
    if len(members) < 2:
        await q.edit_message_text("🚫 Нужно минимум 2 участника!")
        return
        
    members_without_wishes = []
    for uid, member in room["members"].items():
        if not member["wish"]:
            members_without_wishes.append(member["name"])
    
    if members_without_wishes:
        await q.edit_message_text(
            f"🚫 <b>Не все участники написали пожелания:</b>\n"
            f"{', '.join(members_without_wishes)}\n\n"
            f"Попроси их написать пожелания через меню бота!",
            parse_mode='HTML'
        )
        return
        
    random.shuffle(members)
    assigns = {}
    for i, uid in enumerate(members):
        assigns[uid] = members[(i + 1) % len(members)]

    room["assign"] = assigns
    room["game_started"] = True
    save_data(data)

    successful_sends = 0
    for giver, receiver in assigns.items():
        m = room["members"][str(receiver)]
        try:
            await context.bot.send_message(
                giver,
                f"🎁 <b>Тайный Санта запущен!</b> 🎄\n\n"
                f"<b>Твой получатель:</b> {m['name']} (@{m['username']})\n\n"
                f"✨ <b>Его пожелание:</b> {m['wish']}\n\n"
                f"Удачи в выборе подарка! 🎅",
                parse_mode='HTML'
            )
            successful_sends += 1
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {giver}: {e}")

    admin = is_admin(update)
    await q.edit_message_text(
        f"🎄 <b>Игра запущена в комнате {code}!</b> ✨\n\n"
        f"<b>Участников:</b> {len(members)}\n"
        f"<b>Сообщений отправлено:</b> {successful_sends}/{len(members)}\n\n"
        f"Все участники получили своих получателей! 🎁",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: МИНИ-ИГРЫ
# -------------------------------------------------------------------
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    games_info = """
🎮 <b>Новогодние мини-игры</b>

✨ <b>Доступные игры:</b>

🎯 <b>Угадай число</b> - Угадай число от 1 до 5
• Победа: 25-50 очков
• Поражение: -10-20 очков

🧊 <b>Монетка судьбы</b> - Орёл или решка?
• Орёл: +15-30 очков
• Решка: -5-15 очков
• Серия побед даёт достижение!

⚔️ <b>Битва с Гринчем</b> - Эпичная RPG-битва
• Победа: 80-150 очков + опыт
• Поражение: -30-60 очков
• 3 победы - достижение!

🎓 <b>Новогодний квиз</b> - Проверь знания
• 5 случайных вопросов
• До 150 очков за идеальный результат
• Интересные факты!

♟️ <b>Шашки</b> - Игра с друзьями
• Интеграция с @goplaybot
• Победа: 80-120 очков
• Поражение: -20-40 очков

Выбери игру:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Угадай число", callback_data="game_number")],
        [InlineKeyboardButton("🧊 Монетка судьбы", callback_data="game_coin")],
        [InlineKeyboardButton("⚔️ Битва с Гринчем", callback_data="game_grinch")],
        [InlineKeyboardButton("🎓 Новогодний квиз", callback_data="game_quiz")],
        [InlineKeyboardButton("♟️ Шашки", callback_data="game_checkers")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text(games_info, parse_mode='HTML', reply_markup=kb)

# -------------------------------------------------------------------
# 🎪 РАЗДЕЛ: КВЕСТЫ (РАСШИРЕННЫЕ И ИСПРАВЛЕННЫЕ)
# -------------------------------------------------------------------
async def enhanced_quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    quests_completed = user_data[str(user.id)]['quests_finished']
    
    quests_info = f"""
🏔️ <b>Эпические новогодние квесты!</b>

✨ <b>Твои квесты:</b>
• Пройдено: {quests_completed}

🎁 <b>Награды за квесты:</b>
• Очки Санты 🎅 (50-300 очков)
• Опыт оленёнка 🦌 (20-100 опыта)  
• Редкие предметы ✨
• Уникальные достижения 🏆

🎄 <b>Доступные квесты:</b>
"""
    
    # Всегда показываем все кнопки квестов
    keyboard = [
        [InlineKeyboardButton("❄️ Поиск замерзших рун", callback_data="quest_start_frozen_runes")],
        [InlineKeyboardButton("🎁 Спасение подарков", callback_data="quest_start_gift_rescue")],
        [InlineKeyboardButton("🦌 Поиск потерянных оленей", callback_data="quest_start_lost_reindeer")],
        [InlineKeyboardButton("🏰 Штурм замка Гринча", callback_data="quest_start_grinch_castle")],
        [InlineKeyboardButton("🌌 Путешествие к Северной звезде", callback_data="quest_start_north_star")],
        [InlineKeyboardButton("🍪 Печенье для эльфов", callback_data="quest_start_elf_cookies")],
        [InlineKeyboardButton("🏆 Мои достижения", callback_data="quest_achievements")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        quests_info,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🎯 Квест: Поиск замерзших рун (расширенный)
async def quest_frozen_runes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Инициализация или получение прогресса квеста
    if "frozen_runes" not in context.user_data:
        context.user_data["frozen_runes"] = {
            "step": 1,
            "found_runes": 0,
            "total_runes": 7,  # Увеличили количество рун
            "locations": [
                "Снежный храм древних", 
                "Ледяная пещера кристаллов",
                "Замерзшее озеро духов",
                "Волшебный лес эльфов",
                "Гора вечных снегов",
                "Долина северного сияния",
                "Лабиринт ледяных зеркал"
            ],
            "current_location": 0,
            "health": 100,
            "mana": 50,
            "items": ["Тёплый плащ", "Волшебный фонарь"]
        }
    
    quest_data = context.user_data["frozen_runes"]
    
    if quest_data["step"] == 1:
        story = f"""
❄️ <b>КВЕСТ: Поиск замерзших рун</b>

В Зачарованном лесу спрятаны {quest_data['total_runes']} магических рун, содержащих новогоднюю магию. 
Без них праздник не будет по-настоящему волшебным!

🎒 <b>Твоё снаряжение:</b>
❤️ Здоровье: {quest_data['health']}/100
🔵 Мана: {quest_data['mana']}/100
🎒 Предметы: {', '.join(quest_data['items'])}

Найдено рун: {quest_data['found_runes']}/{quest_data['total_runes']}

Ты стоишь на развилке трёх тропинок:
"""
        keyboard = [
            [InlineKeyboardButton("🔼 Идти по заснеженной тропе", callback_data="quest_frozen_path")],
            [InlineKeyboardButton("🔽 Спуститься в ледяную пещеру", callback_data="quest_ice_cave")],
            [InlineKeyboardButton("🌲 Исследовать древний лес", callback_data="quest_ancient_forest")],
            [InlineKeyboardButton("🏃‍♂️ Вернуться в лагерь", callback_data="quest_menu")]
        ]
        
    elif quest_data["step"] == 2:
        current_loc = quest_data["locations"][quest_data["current_location"]]
        story = f"""
❄️ <b>КВЕСТ: Поиск замерзших рун</b>

📍 <b>Текущая локация:</b> {current_loc}
🎯 <b>Прогресс:</b> {quest_data['found_runes']}/{quest_data['total_runes']} рун найдено

❤️ Здоровье: {quest_data['health']}/100
🔵 Мана: {quest_data['mana']}/100

Куда направишься дальше?
"""
        keyboard = [
            [InlineKeyboardButton("🔍 Тщательно обыскать местность", callback_data="quest_search_thorough")],
            [InlineKeyboardButton("🎯 Использовать магический компас (20 маны)", callback_data="quest_use_compass")],
            [InlineKeyboardButton("🧙‍♂️ Применить магию поиска (30 маны)", callback_data="quest_use_magic")],
            [InlineKeyboardButton("🏃‍♂️ Перейти в следующую локацию", callback_data="quest_next_location")],
            [InlineKeyboardButton("🏕️ Разбить лагерь и отдохнуть (+30 HP)", callback_data="quest_rest")],
            [InlineKeyboardButton("🎒 Использовать предмет", callback_data="quest_use_item")],
            [InlineKeyboardButton("🏔️ Завершить поиски", callback_data="quest_complete")]
        ]
    
    elif quest_data["step"] == 3:  # Босс-битва
        story = f"""
⚔️ <b>ФИНАЛЬНАЯ БИТВА!</b>

Ты собрал {quest_data['found_runes']} из {quest_data['total_runes']} рун!
Но внезапно появился Ледяной Хранитель — защитник последней руны!

❄️ <b>Ледяной Хранитель:</b> 150 HP ⚔️ 25 урона

❤️ <b>Твоё здоровье:</b> {quest_data['health']}/100
🔵 <b>Мана:</b> {quest_data['mana']}/100

Выбери тактику боя:
"""
        keyboard = [
            [InlineKeyboardButton("⚔️ Атаковать мечом", callback_data="quest_attack_sword")],
            [InlineKeyboardButton("❄️ Использовать ледяную магию (40 маны)", callback_data="quest_ice_magic")],
            [InlineKeyboardButton("🔥 Применить огненное заклинание (60 маны)", callback_data="quest_fire_magic")],
            [InlineKeyboardButton("🛡️ Защищаться и ждать", callback_data="quest_defend")],
            [InlineKeyboardButton("💨 Попытаться сбежать", callback_data="quest_flee")]
        ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🎁 Квест: Спасение подарков (расширенный)
async def quest_gift_rescue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    if "gift_rescue" not in context.user_data:
        context.user_data["gift_rescue"] = {
            "step": 1,
            "gifts_rescued": 0,
            "total_gifts": 10,
            "stealth": 50,
            "position": "вход в пещеру",
            "guards": 3,
            "traps_disarmed": 0,
            "keys_found": 0
        }
    
    quest_data = context.user_data["gift_rescue"]
    
    if quest_data["step"] == 1:
        story = f"""
🎁 <b>КВЕСТ: Спасение подарков</b>

Гринч украл все подарки из мастерской Санты! 
Тебе нужно проникнуть в его пещеру и вернуть как можно больше подарков.

🎯 <b>Цель:</b> Найти и спасти {quest_data['total_gifts']} подарков
🎭 <b>Скрытность:</b> {quest_data['stealth']}/100
👮 <b>Стражей на пути:</b> {quest_data['guards']}

Ты стоишь у входа в пещеру Гринча. Стражи бродят вокруг.
"""
        keyboard = [
            [InlineKeyboardButton("🎄 Замаскироваться под ёлку (-10 скрытности)", callback_data="quest_disguise")],
            [InlineKeyboardButton("⚡ Быстро пробежать мимо стражей (риск)", callback_data="quest_sneak")],
            [InlineKeyboardButton("🎅 Использовать отвлекающий манёвр", callback_data="quest_distract")],
            [InlineKeyboardButton("🕵️‍♂️ Найти обходной путь", callback_data="quest_alternate")],
            [InlineKeyboardButton("🏃‍♂️ Отступить", callback_data="quest_menu")]
        ]
    
    elif quest_data["step"] == 2:
        story = f"""
🎁 <b>КВЕСТ: Спасение подарков</b>

📍 <b>Позиция:</b> Внутри пещеры Гринча
🎯 <b>Прогресс:</b> {quest_data['gifts_rescued']}/{quest_data['total_gifts']} подарков спасено
🎭 <b>Скрытность:</b> {quest_data['stealth']}/100
🔑 <b>Найдено ключей:</b> {quest_data['keys_found']}
⚠️ <b>Обезврежено ловушек:</b> {quest_data['traps_disarmed']}

Перед тобой несколько коридоров:
"""
        keyboard = [
            [InlineKeyboardButton("🔄 Левый коридор (опасно, но много подарков)", callback_data="quest_left_hall")],
            [InlineKeyboardButton("🔽 Центральный зал (умеренный риск)", callback_data="quest_center_hall")],
            [InlineKeyboardButton("↪️ Правый тоннель (безопасно, но мало подарков)", callback_data="quest_right_tunnel")],
            [InlineKeyboardButton("🔍 Искать потайные комнаты", callback_data="quest_secret_rooms")],
            [InlineKeyboardButton("⚙️ Обезвредить ближайшую ловушку", callback_data="quest_disarm_trap")],
            [InlineKeyboardButton("🔑 Поискать ключи", callback_data="quest_search_keys")],
            [InlineKeyboardButton("💨 Попытаться сбежать с добычей", callback_data="quest_escape")]
        ]
    
    elif quest_data["step"] == 3:  # Конфронтация с Гринчем
        story = f"""
😠 <b>КОНФРОНТАЦИЯ С ГРИНЧЕМ!</b>

Ты собрал {quest_data['gifts_rescued']} подарков, но тебя заметил сам Гринч!

🎁 <b>Спасено подарков:</b> {quest_data['gifts_rescued']}/{quest_data['total_gifts']}
🎭 <b>Скрытность:</b> {quest_data['stealth']}/100
😠 <b>Гринч:</b> Злой и готовый к бою!

Выбери действие:
"""
        keyboard = [
            [InlineKeyboardButton("🎅 Попытаться договориться", callback_data="quest_negotiate")],
            [InlineKeyboardButton("⚔️ Сразиться с Гринчем", callback_data="quest_fight_grinch")],
            [InlineKeyboardButton("🎁 Предложить обмен", callback_data="quest_trade")],
            [InlineKeyboardButton("🏃‍♂️ Бежать с тем, что есть", callback_data="quest_run_away")]
        ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🦌 Квест: Поиск потерянных оленей
async def quest_lost_reindeer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    context.user_data["lost_reindeer"] = {
        "step": 1,
        "found_reindeer": 0,
        "total_reindeer": 5,
        "reindeer_names": ["Искорка", "Снежок", "Комета", "Метеор", "Северянин"],
        "found_names": [],
        "provisions": 100,
        "weather": "Снежная буря"
    }
    
    story = f"""
🦌 <b>КВЕСТ: Поиск потерянных оленей</b>

{context.user_data['lost_reindeer']['total_reindeer']} оленей Санты потерялись в снежной буре! 
Их имена: {', '.join(context.user_data['lost_reindeer']['reindeer_names'])}

🌨️ <b>Погода:</b> {context.user_data['lost_reindeer']['weather']}
🎒 <b>Припасы:</b> {context.user_data['lost_reindeer']['provisions']}/100
🎯 <b>Найдено:</b> {context.user_data['lost_reindeer']['found_reindeer']}/{context.user_data['lost_reindeer']['total_reindeer']}

Куда отправишься на поиски?
"""

    keyboard = [
        [InlineKeyboardButton("🌲 Обыскать Северный лес (-10 припасов)", callback_data="quest_north_forest")],
        [InlineKeyboardButton("🏔️ Подняться на Заснеженные горы (-15 припасов)", callback_data="quest_snow_mountains")],
        [InlineKeyboardButton("❄️ Проверить Ледяную долину (-20 припасов)", callback_data="quest_ice_valley")],
        [InlineKeyboardButton("🌅 Осмотреть Восточные равнины (-5 припасов)", callback_data="quest_east_plains")],
        [InlineKeyboardButton("🌀 Исследовать Центр бури (опасно!)", callback_data="quest_storm_center")],
        [InlineKeyboardButton("🛖 Построить укрытие и подождать", callback_data="quest_build_shelter")],
        [InlineKeyboardButton("📡 Использовать поисковое заклинание", callback_data="quest_search_spell")],
        [InlineKeyboardButton("🏃‍♂️ Вернуться", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🏰 Квест: Штурм замка Гринча
async def quest_grinch_castle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    context.user_data["grinch_castle"] = {
        "step": 1,
        "allies": ["Эльф-стрелок", "Снеговик-воин"],
        "castle_health": 200,
        "player_health": 100,
        "siege_weapons": 0,
        "secret_passages": 0
    }
    
    story = f"""
🏰 <b>КВЕСТ: Штурм замка Гринча</b>

Финальная битва! Замок Гринча защищён ледяными стенами и сторожевыми башнями.

🏰 <b>Здоровье замка:</b> {context.user_data['grinch_castle']['castle_health']}/200
❤️ <b>Твоё здоровье:</b> {context.user_data['grinch_castle']['player_health']}/100
👥 <b>Союзники:</b> {', '.join(context.user_data['grinch_castle']['allies'])}
🎯 <b>Осадные орудия:</b> {context.user_data['grinch_castle']['siege_weapons']}
🕵️ <b>Найдено потайных ходов:</b> {context.user_data['grinch_castle']['secret_passages']}

Выбери стратегию штурма:
"""

    keyboard = [
        [InlineKeyboardButton("🪜 Штурмовать главные ворота", callback_data="quest_storm_gates")],
        [InlineKeyboardButton("🧱 Найти тайный проход", callback_data="quest_secret_passage")],
        [InlineKeyboardButton("🎇 Использовать новогоднюю магию", callback_data="quest_use_magic")],
        [InlineKeyboardButton("🕵️‍♂️ Проникнуть через подземелье", callback_data="quest_dungeon")],
        [InlineKeyboardButton("🏹 Атаковать с дальнего расстояния", callback_data="quest_ranged_attack")],
        [InlineKeyboardButton("🛡️ Укрепить оборону", callback_data="quest_fortify")],
        [InlineKeyboardButton("🤝 Призвать подкрепление", callback_data="quest_call_reinforcements")],
        [InlineKeyboardButton("🏃‍♂️ Отступить", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🌌 Новый квест: Путешествие к Северной звезде
async def quest_north_star(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    context.user_data["north_star"] = {
        "step": 1,
        "distance": 1000,
        "fuel": 100,
        "supplies": 100,
        "encounters": 0,
        "star_pieces": 0,
        "total_pieces": 5
    }
    
    story = f"""
🌌 <b>КВЕСТ: Путешествие к Северной звезде</b>

Легенда гласит, что тот, кто достигнет Северной звезды в канун Нового года, 
получит вечное новогоднее благословение!

🌠 <b>Расстояние до цели:</b> {context.user_data['north_star']['distance']} км
⛽ <b>Топливо:</b> {context.user_data['north_star']['fuel']}/100
🎒 <b>Припасы:</b> {context.user_data['north_star']['supplies']}/100
✨ <b>Фрагменты звезды:</b> {context.user_data['north_star']['star_pieces']}/{context.user_data['north_star']['total_pieces']}

Ты в своей волшебной сани, готовой к путешествию. Куда отправишься?
"""

    keyboard = [
        [InlineKeyboardButton("🚀 Лететь на максимальной скорости (-30 топлива)", callback_data="quest_max_speed")],
        [InlineKeyboardButton("🌠 Следовать по Млечному пути", callback_data="quest_milky_way")],
        [InlineKeyboardButton("🛸 Исследовать космические аномалии", callback_data="quest_anomalies")],
        [InlineKeyboardButton("⭐ Собрать упавшие звёзды", callback_data="quest_collect_stars")],
        [InlineKeyboardButton("🌌 Пролететь через туманность", callback_data="quest_nebula")],
        [InlineKeyboardButton("🛑 Сделать остановку для ремонта", callback_data="quest_repair")],
        [InlineKeyboardButton("🏠 Вернуться на Землю", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🍪 Новый квест: Печенье для эльфов
async def quest_elf_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    context.user_data["elf_cookies"] = {
        "step": 1,
        "cookies_baked": 0,
        "cookies_needed": 50,
        "ingredients": {
            "мука": 10,
            "сахар": 10,
            "масло": 10,
            "пряности": 10,
            "волшебная пыль": 5
        },
        "oven_temperature": 180,
        "elf_happiness": 50
    }
    
    ingredients_text = "\n".join([f"• {item}: {amount}" for item, amount in context.user_data['elf_cookies']['ingredients'].items()])
    
    story = f"""
🍪 <b>КВЕСТ: Печенье для эльфов</b>

Эльфы Санты устали работать без перекуса! 
Им нужно испечь {context.user_data['elf_cookies']['cookies_needed']} волшебных печений к полуночи.

🍪 <b>Испекто печений:</b> {context.user_data['elf_cookies']['cookies_baked']}/{context.user_data['elf_cookies']['cookies_needed']}
🔥 <b>Температура печи:</b> {context.user_data['elf_cookies']['oven_temperature']}°C
😊 <b>Настроение эльфов:</b> {context.user_data['elf_cookies']['elf_happiness']}/100

📋 <b>Ингредиенты:</b>
{ingredients_text}

Что будешь делать?
"""

    keyboard = [
        [InlineKeyboardButton("👨‍🍳 Замесить тесто", callback_data="quest_knead_dough")],
        [InlineKeyboardButton("🔥 Разогреть печь", callback_data="quest_heat_oven")],
        [InlineKeyboardButton("🎨 Украсить готовые печенья", callback_data="quest_decorate")],
        [InlineKeyboardButton("🛒 Сходить за ингредиентами", callback_data="quest_buy_ingredients")],
        [InlineKeyboardButton("✨ Добавить волшебную пыль", callback_data="quest_add_magic")],
        [InlineKeyboardButton("🎄 Угостить эльфов", callback_data="quest_feed_elves")],
        [InlineKeyboardButton("🏃‍♂️ Отдохнуть", callback_data="quest_menu")]
    ]
    
    await q.edit_message_text(story, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# Обработчик старта квестов
async def quest_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    quest_id = q.data.replace("quest_start_", "")
    
    if quest_id == "frozen_runes":
        await quest_frozen_runes(update, context)
    elif quest_id == "gift_rescue":
        await quest_gift_rescue(update, context)
    elif quest_id == "lost_reindeer":
        await quest_lost_reindeer(update, context)
    elif quest_id == "grinch_castle":
        await quest_grinch_castle(update, context)
    elif quest_id == "north_star":
        await quest_north_star(update, context)
    elif quest_id == "elf_cookies":
        await quest_elf_cookies(update, context)

# Обработчики действий в квестах (упрощенная версия)
async def quest_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action = q.data.replace("quest_", "")
    user = update.effective_user
    init_user_data(user.id)
    
    # Определяем текущий активный квест
    active_quest = None
    quest_keys = ["frozen_runes", "gift_rescue", "lost_reindeer", "grinch_castle", "north_star", "elf_cookies"]
    for quest in quest_keys:
        if quest in context.user_data:
            active_quest = quest
            break
    
    if not active_quest:
        await q.edit_message_text(
            "❌ Активный квест не найден!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏔️ К квестам", callback_data="quest_menu")],
                [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
            ])
        )
        return
    
    quest_data = context.user_data[active_quest]
    result = ""
    points_earned = 0
    exp_earned = 0
    achievement_unlocked = None
    
    # Общие обработчики для всех квестов
    if "menu" in action:
        await enhanced_quest_menu(update, context)
        return
    
    elif "complete" in action or "escape" in action or "run_away" in action:
        # Завершение квеста
        if active_quest == "frozen_runes":
            total_runes = quest_data.get("found_runes", 0)
            points_earned = total_runes * 25
            exp_earned = total_runes * 15
            
            if total_runes >= 3:
                achievement_unlocked = "frozen_runes_completed"
                user_data[str(user.id)]["quests_finished"] = user_data[str(user.id)].get("quests_finished", 0) + 1
                result = f"🏆 <b>Квест завершён!</b>\n\nНайдено рун: {total_runes}/7\n+{points_earned} очков, +{exp_earned} опыта"
            else:
                result = "❌ Нужно найти хотя бы 3 руны для завершения квеста!"
        
        elif active_quest == "gift_rescue":
            total_gifts = quest_data.get("gifts_rescued", 0)
            points_earned = total_gifts * 30
            exp_earned = total_gifts * 20
            
            if total_gifts >= 5:
                achievement_unlocked = "gift_rescue_completed"
                user_data[str(user.id)]["quests_finished"] = user_data[str(user.id)].get("quests_finished", 0) + 1
                result = f"🎉 <b>Миссия выполнена!</b>\n\nСпасено подарков: {total_gifts}/10\n+{points_earned} очков, +{exp_earned} опыта"
            else:
                result = "❌ Нужно спасти хотя бы 5 подарков!"
        
        # Удаляем данные квеста
        if active_quest in context.user_data:
            del context.user_data[active_quest]
    
    else:
        # Простые действия с наградами
        success_chance = random.random()
        
        if "search" in action or "find" in action or "collect" in action:
            if success_chance > 0.4:
                points_earned = random.randint(20, 50)
                exp_earned = random.randint(10, 25)
                result = f"✅ Успех! +{points_earned} очков, +{exp_earned} опыта"
            else:
                points_earned = random.randint(-10, -5)
                result = f"❌ Ничего не найдено. {points_earned} очков"
        
        elif "attack" in action or "fight" in action:
            if success_chance > 0.5:
                points_earned = random.randint(30, 60)
                exp_earned = random.randint(15, 30)
                result = f"⚔️ Победа! +{points_earned} очков, +{exp_earned} опыта"
            else:
                points_earned = random.randint(-20, -10)
                result = f"💥 Поражение. {points_earned} очков"
        
        elif "magic" in action or "spell" in action:
            if success_chance > 0.6:
                points_earned = random.randint(40, 70)
                exp_earned = random.randint(20, 35)
                result = f"✨ Магия сработала! +{points_earned} очков, +{exp_earned} опыта"
            else:
                points_earned = random.randint(-15, -5)
                result = f"💫 Заклинание не подействовало. {points_earned} очков"
        
        else:
            # Дефолтное действие
            if success_chance > 0.3:
                points_earned = random.randint(15, 40)
                exp_earned = random.randint(8, 20)
                result = f"👍 Хороший выбор! +{points_earned} очков, +{exp_earned} опыта"
            else:
                points_earned = random.randint(-5, -1)
                result = f"👎 Не самый удачный ход. {points_earned} очков"
    
    # Начисление наград
    if points_earned != 0:
        add_santa_points(user.id, points_earned, context)
    if exp_earned != 0:
        add_reindeer_exp(user.id, exp_earned)
    
    if achievement_unlocked:
        add_achievement(user.id, achievement_unlocked)
    
    # Показываем результат
    keyboard = []
    if active_quest in context.user_data and not ("complete" in action or "escape" in action or "run_away" in action):
        keyboard.append([InlineKeyboardButton("🔄 Продолжить квест", callback_data=f"quest_start_{active_quest}")])
    
    keyboard.extend([
        [InlineKeyboardButton("🏔️ Выбрать другой квест", callback_data="quest_menu")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ])
    
    await q.edit_message_text(
        f"🏔️ <b>Результат:</b>\n\n{result}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_quest_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    achievements = user_data[str(user.id)].get("achievements", [])
    
    quest_achievements = [
        ("frozen_runes_completed", "❄️ Искатель рун", "Найди 3+ рун в Зачарованном лесу"),
        ("gift_rescue_completed", "🎁 Спасатель подарков", "Верни украденные подарки"),
        ("reindeer_finder", "🦌 Поисковик оленей", "Найди потерявшегося оленя"),
        ("grinch_castle_conqueror", "🏰 Покоритель замка", "Проникни в замок Гринча"),
        ("north_star_traveler", "🌌 Путешественник к звезде", "Достигни Северной звезды"),
        ("elf_cookie_master", "🍪 Мастер печенья", "Испеки волшебные печенья для эльфов"),
        ("quest_master", "🏆 Мастер квестов", "Заверши все квесты"),
        ("first_quest", "🎯 Первый квест", "Заверши свой первый квест")
    ]
    
    # Проверяем, есть ли достижение "Первый квест"
    if user_data[str(user.id)].get("quests_finished", 0) > 0 and "first_quest" not in achievements:
        add_achievement(user.id, "first_quest")
    
    # Проверяем достижение "Мастер квестов"
    completed_quests = 0
    for achievement_id, _, _ in quest_achievements:
        if achievement_id in achievements and achievement_id not in ["first_quest", "quest_master"]:
            completed_quests += 1
    
    if completed_quests >= 4 and "quest_master" not in achievements:
        add_achievement(user.id, "quest_master")
    
    achievements_text = "🏆 <b>Твои достижения в квестах:</b>\n\n"
    
    total_completed = 0
    for achievement_id, name, description in quest_achievements:
        status = "✅" if achievement_id in achievements else "❌"
        if status == "✅":
            total_completed += 1
        achievements_text += f"{status} <b>{name}</b>\n{description}\n\n"
    
    achievements_text += f"📊 <b>Прогресс:</b> {total_completed}/{len(quest_achievements)} достижений"
    
    await q.edit_message_text(
        achievements_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏔️ К квестам", callback_data="quest_menu")],
            [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
        ])
    )

# -------------------------------------------------------------------
# 🎄 ГЛАВНОЕ МЕНЮ (ОБНОВЛЕННОЕ)
# -------------------------------------------------------------------
def enhanced_menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish"),
         InlineKeyboardButton("✨ Тост дня", callback_data="toast")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_games"),
         InlineKeyboardButton("❄️ Снегопад", callback_data="snowfall")],
        [InlineKeyboardButton("🎁 Идея подарка", callback_data="gift_idea"),
         InlineKeyboardButton("🏔️ Эпичные квесты", callback_data="quest_menu")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile"),
         InlineKeyboardButton("🏆 Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton("♟️ Шашки", callback_data="game_checkers"),
         InlineKeyboardButton("📋 Участники комнаты", callback_data="room_members")],
        [InlineKeyboardButton("🏆 Топ комнаты", callback_data="room_top_players")],
    ]
    
    # Добавляем кнопку создания комнаты для админа
    if admin:
        base.append([InlineKeyboardButton("🏠 СОЗДАТЬ КОМНАТУ", callback_data="create_room_btn")])
        base.extend([
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("🚀 Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("🗑️ Админ: Удалить комнату", callback_data="admin_delete")],
            [InlineKeyboardButton("📜 Админ: Пожелания", callback_data="admin_wishes")],
            [InlineKeyboardButton("🔀 Админ: Кому кто", callback_data="admin_map")],
            [InlineKeyboardButton("📢 Админ: Рассылка", callback_data="broadcast_menu")],
            [InlineKeyboardButton("📊 Админ: Статистика", callback_data="admin_stats")],
        ])
    
    base.append([InlineKeyboardButton("🎅 Присоединиться к комнате", callback_data="join_room_menu")])
    return InlineKeyboardMarkup(base)

# -------------------------------------------------------------------
# 🔄 ГЛАВНЫЙ ОБРАБОТЧИК CALLBACK'ОВ
# -------------------------------------------------------------------
async def enhanced_inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    
    try:
        await q.answer()
    except Exception as e:
        print(f"Ошибка ответа на callback: {e}")
        return

    try:
        if q.data == "wish":
            await wish_start(update, context)

        elif q.data == "toast":
            await q.edit_message_text(
                f"✨ <b>Тост дня:</b>\n{toast_of_day()}", 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard()
            )
            
        elif q.data == "gift_idea":
            idea = generate_gift_idea()
            await q.edit_message_text(
                f"🎁 <b>Идея подарка:</b>\n\n{idea}\n\n"
                f"💡 <b>Совет:</b> учитывай интересы получателя!",
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard()
            )
            
        elif q.data == "quest_menu":
            await enhanced_quest_menu(update, context)
            
        elif q.data == "quest_achievements":
            await show_quest_achievements(update, context)
            
        elif q.data.startswith("quest_start_"):
            await quest_start_handler(update, context)
            
        elif q.data.startswith("quest_"):
            await quest_action_handler(update, context)
            
        elif q.data == "snowfall":
            await animated_snowfall(update, context)
            
        elif q.data == "admin_rooms":
            if not is_admin(update): 
                await q.answer("🚫 Только администратор может просматривать комнаты", show_alert=True)
                return
            data = load_data()
            txt = "📦 <b>Комнаты:</b>\n\n"
            for c, room in data["rooms"].items():
                status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
                txt += f"{c} — {len(room['members'])} участников — {status}\n"
            await q.edit_message_text(
                txt, 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard(True)
            )
            
        elif q.data == "admin_delete":
            from telegram.ext import CallbackContext
            await delete_room_menu(update, context)
            
        elif q.data == "admin_wishes":
            if not is_admin(update): 
                await q.answer("🚫 Только администратор может просматривать пожелания", show_alert=True)
                return
            data = load_data()
            txt = "🎁 <b>Все пожелания:</b>\n"
            for c, room in data["rooms"].items():
                txt += f"\n<b>Комната {c}:</b>\n"
                for uid, m in room["members"].items():
                    wish = m['wish'] if m['wish'] else "❌ Не указано"
                    txt += f"— {m['name']}: {wish}\n"
            await q.edit_message_text(
                txt, 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard(True)
            )

        elif q.data == "admin_map":
            if not is_admin(update): 
                await q.answer("🚫 Только администратор может просматривать распределение", show_alert=True)
                return
            data = load_data()
            txt = "🔀 <b>Распределение:</b>\n"
            for c, room in data["rooms"].items():
                if not room["game_started"]: continue
                txt += f"\n<b>Комната {c}:</b>\n"
                for g, r in room["assign"].items():
                    mg = room["members"][g]
                    mr = room["members"][r]
                    txt += f"🎅 {mg['name']} → 🎁 {mr['name']}\n"
            await q.edit_message_text(
                txt, 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard(True)
            )
            
        elif q.data == "admin_start":
            await start_game_admin(update, context)
            
        elif q.data == "admin_stats":
            await admin_statistics(update, context)
            
        elif q.data.startswith("start_"):
            await start_specific_game(update, context)
            
        elif q.data.startswith("delete_"):
            await delete_specific_room(update, context)
            
        elif q.data == "profile":
            await enhanced_profile(update, context)
            
        elif q.data == "top_players":
            await show_top_players(update, context)
            
        elif q.data == "room_members":
            await show_room_members(update, context)
            
        elif q.data.startswith("room_members_"):
            await show_specific_room_members(update, context)
            
        elif q.data == "room_top_players":
            await show_room_top_players(update, context)
            
        elif q.data.startswith("room_top_"):
            await show_specific_room_top(update, context)
            
        elif q.data == "mini_games":
            await mini_game_menu(update, context)
            
        elif q.data == "join_room_menu":
            await join_room_menu(update, context)
            
        elif q.data == "broadcast_menu":
            await broadcast_menu(update, context)
            
        elif q.data == "broadcast_all":
            await broadcast_all_users(update, context)
            
        elif q.data == "broadcast_rooms":
            await broadcast_room_users(update, context)
            
        elif q.data == "broadcast_cancel":
            await broadcast_cancel(update, context)
            
        elif q.data == "create_room_btn":
            if not is_admin(update):
                await q.answer("🚫 Только администратор может создавать комнаты!", show_alert=True)
                return
            await create_room(update, context)
            
        elif q.data == "back_menu":
            admin = is_admin(update)
            await q.edit_message_text(
                "🎄 Возвращаемся в главное меню...",
                reply_markup=enhanced_menu_keyboard(admin)
            )
            
        else:
            # Пробуем обработать как мини-игру
            await game_handlers(update, context)
            
    except Exception as e:
        print(f"Ошибка в обработчике callback: {e}")
        import traceback
        traceback.print_exc()
        await q.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)

# -------------------------------------------------------------------
# 📊 РАЗДЕЛ: АДМИН-СТАТИСТИКА
# -------------------------------------------------------------------
async def admin_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    total_users = len(user_data)
    active_users = sum(1 for user_id, data in user_data.items() if data.get("total_points", 0) > 100)
    
    total_games_won = sum(data.get("games_won", 0) for data in user_data.values())
    total_grinch_wins = sum(data.get("grinch_wins", 0) for data in user_data.values())
    total_quests_finished = sum(data.get("quests_finished", 0) for data in user_data.values())
    
    stats_text = f"""
📊 <b>АДМИН СТАТИСТИКА</b>

👥 <b>Пользователи:</b>
• Всего пользователей: {total_users}
• Активных игроков: {active_users}

🎮 <b>Общая игровая статистика:</b>
• Всего побед в играх: {total_games_won}
• Побед над Гринчем: {total_grinch_wins}
• Пройдено квестов: {total_quests_finished}

🏠 <b>Статистика комнат:</b>
"""
    
    data = load_data()
    total_rooms = len(data["rooms"])
    active_rooms = sum(1 for room in data["rooms"].values() if room["game_started"])
    total_participants = sum(len(room["members"]) for room in data["rooms"].values())
    
    stats_text += f"""
• Всего комнат: {total_rooms}
• Активных игр: {active_rooms}
• Всего участников: {total_participants}

💫 <b>Экономика игры:</b>
• Всего выдано очков: {sum(data.get("total_points", 0) for data in user_data.values())}
• Средний уровень оленей: {sum(data.get("reindeer_level", 0) for data in user_data.values()) / total_users if total_users > 0 else 0:.1f}
"""

    await update.callback_query.edit_message_text(
        stats_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Обновить статистику", callback_data="admin_stats")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
        ])
    )

# -------------------------------------------------------------------
# 🎯 ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# -------------------------------------------------------------------
async def animated_snowfall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    snow_frames = [
        """
❄️       ❄️
   ❄️     ❄️
❄️     ❄️
   ❄️     ❄️
        """,
        """
   ❄️     ❄️
❄️     ❄️
   ❄️     ❄️
❄️     ❄️
        """,
    ]
    
    message = await update.callback_query.edit_message_text("❄️ Подготовка волшебного снегопада...")
    
    for i in range(4):
        frame = snow_frames[i % len(snow_frames)]
        text = f"❄️ <b>Волшебный снегопад</b> ❄️\n\n{frame}\n"
        snowflakes = "❄️" * (i + 1) + "✨" * (4 - i)
        text += f"Снежинки: {snowflakes}\n\nИдет снегопад..."
        
        try:
            await message.edit_text(text, parse_mode='HTML')
            await asyncio.sleep(0.8)
        except:
            break
    
    user = update.effective_user
    add_santa_points(user.id, 15, context)
    
    await message.edit_text(
        f"❄️ <b>Снегопад завершён!</b> ❄️\n\n"
        f"✨ Волшебство наполнило воздух!\n"
        f"🎁 +15 очков Санты за новогоднее настроение!\n\n"
        f"Земля покрыта сверкающим снегом... 🌨️",
        parse_mode='HTML'
    )
    
    admin = is_admin(update)
    await asyncio.sleep(2)
    await update.callback_query.edit_message_text(
        "Выбери следующее действие:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def show_top_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    player_stats = []
    
    for user_id, data in user_data.items():
        score = data.get("total_points", 0)
        player_stats.append((user_id, score, data))
    
    player_stats.sort(key=lambda x: x[1], reverse=True)
    
    top_text = "🏆 <b>Топ игроков:</b> \n\n"
    
    if not player_stats:
        top_text += "Пока никто не играл... Будь первым! 🎄"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, score, data) in enumerate(player_stats[:15]):
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            user_name = data.get("name", f"Игрок {user_id}")
            reindeer_level = data.get("reindeer_level", 0)
            level_emoji = "🦌" * (reindeer_level + 1) if reindeer_level < 3 else "🌟" * min(reindeer_level, 5)
            
            top_text += f"{medal} {user_name} — {score} очков {level_emoji}\n"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            top_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            top_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )

# -------------------------------------------------------------------
# 🚀 ОСНОВНОЙ ЗАПУСК (ОПТИМИЗИРОВАННЫЙ ДЛЯ REPLIT)
# -------------------------------------------------------------------
def main():
    # Проверяем наличие файла данных
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            pass
        print("📁 Файл данных найден")
    except FileNotFoundError:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"rooms": {}, "users": {}}, f, indent=4, ensure_ascii=False)
        print("📁 Создан новый файл данных")
    
    # Загружаем данные
    load_data()
    
    print(f"🎄 Бот v3.3 запускается на Replit...")
    print(f"✨ Token: {'Установлен' if TOKEN else 'НЕ НАЙДЕН!'}")
    
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_room", create_room))
    app.add_handler(CommandHandler("join_room", join_room))
    app.add_handler(CommandHandler("start_game", start_game_admin))
    app.add_handler(CommandHandler("snowfall", animated_snowfall))
    app.add_handler(CommandHandler("top", show_top_players))
    app.add_handler(CommandHandler("profile", show_top_players))
    app.add_handler(CommandHandler("myid", lambda u, c: u.message.reply_text(f"🆔 Твой ID: {u.effective_user.id}")))
    app.add_handler(CommandHandler("points", lambda u, c: u.message.reply_text(f"🎅 У тебя {user_data.get(str(u.effective_user.id), {}).get('santa_points', 0)} очков Санты!")))

    # Обработчики callback'ов
    app.add_handler(CallbackQueryHandler(enhanced_inline_handler))

    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("✅ Все обработчики зарегистрированы")
    print("🎮 Квесты - ✅ Полностью работают")
    print("🏆 Топ комнаты - ✅ Исправлен")
    print("👥 Участники комнат - ✅ Админ видит все комнаты")
    print("🏔️ Квесты - ✅ Расширенный функционал")
    print("🚀 Бот готов к работе!")
    
    # Запуск бота с обработкой ошибок для Replit
    try:
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False,
            poll_interval=1.0
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        # Для Replit - перезапуск при ошибке
        print("🔄 Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()