# 🔥🎄 SUPER-DELUXE SECRET SANTA BOT v3.5 🎄🔥
# Упрощенная версия: удалены лишние мини-игры, оставлены только квиз и битва с Гринчем

import json
import random
import string
import asyncio
import os
import sys
import urllib.request
import tempfile
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
CONGRATS_AUDIO_URL = "OLEN.mp3"

print(f"🎄 Запуск Secret Santa Bot v3.5 на Replit...")
print(f"Токен: {'✅ Установлен' if TOKEN else '❌ НЕ НАЙДЕН!'}")

# Проверка токена
if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не установлен!")
    print("💡 Установите переменную окружения TELEGRAM_TOKEN в Replit Secrets")
    sys.exit(1)

# Единая функция загрузки данных
def load_all_data():
    """Загружает все данные из файла и обновляет глобальную переменную user_data"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            global user_data
            user_data = data["users"]
            return data
    except FileNotFoundError:
        default_data = {"rooms": {}, "users": {}}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        global user_data
        user_data = {}
        return default_data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        global user_data
        user_data = {}
        return {"rooms": {}, "users": {}}

# Обновите функцию save_data
def save_all_data(data):
    """Сохраняет все данные в файл"""
    data["users"] = user_data
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
        return False

user_data = {}

def load_all_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "users" not in data:
                data["users"] = {}
            global user_data
            user_data = data["users"]
            return data
    except FileNotFoundError:
        default_data = {"rooms": {}, "users": {}}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}

def save_all_data(data):
    data["users"] = user_data
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")

def load_all_data():
    """Загружает данные из файла без изменения глобальной переменной user_data"""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {"rooms": {}, "users": {}}
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"rooms": {}, "users": {}}
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

# -------------------------------------------------------------------
# СИСТЕМА ДАННЫХ ПОЛЬЗОВАТЕЛЯ (без очков)
# -------------------------------------------------------------------
def init_user_data(user_id):
    user_id_str = str(user_id)
    
    # Загружаем актуальные данные из файла
    data = load_all_data()
    
    if user_id_str not in user_data:
        # Проверяем, есть ли пользователь в файле
        if user_id_str in data.get("users", {}):
            # Копируем данные из файла
            user_data[user_id_str] = data["users"][user_id_str].copy()
        else:
            # Создаем нового пользователя
            user_data[user_id_str] = {
                "achievements": [],
                "games_won": 0,
                "grinch_fights": 0,
                "grinch_wins": 0,
                "quiz_points": 0,
                "quiz_wins": 0,
                "name": "",
                "username": "",
                "answered_quiz_questions": [],
                "total_quiz_correct": 0,
                "total_quiz_played": 0,
                "congratulated_333": False
            }
    
    # Убедимся, что все необходимые поля существуют
    required_fields = [
        "achievements", "games_won", "grinch_fights", "grinch_wins",
        "quiz_points", "quiz_wins", "name", "username",
        "answered_quiz_questions", "total_quiz_correct", 
        "total_quiz_played", "congratulated_333"
    ]
    
    for field in required_fields:
        if field not in user_data[user_id_str]:
            user_data[user_id_str][field] = [] if field == "achievements" or field == "answered_quiz_questions" else 0 if "int" in str(type(0)) else ""
    
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "achievements": [],
            "games_won": 0,
            "grinch_fights": 0,
            "grinch_wins": 0,
            "quiz_points": 0,
            "quiz_wins": 0,
            "name": "",
            "username": "",
            "answered_quiz_questions": [],
            "total_quiz_correct": 0,
            "total_quiz_played": 0,
            "congratulated_333": False  # <-- ДОБАВЬТЕ ЭТУ СТРОЧКУ
        }

def add_achievement(user_id, achievement_key):
    init_user_data(user_id)
    if achievement_key not in user_data[str(user.id)]["achievements"]:
        user_data[str(user.id)]["achievements"].append(achievement_key)
    
    data = load_all_data()
    data["users"] = user_data
    save_all_data(data)

def is_user_in_room(user_id):
    """Проверяет, находится ли пользователь в какой-либо комнате"""
    data = load_all_data()
    for code, room in data["rooms"].items():
        if str(user_id) in room["members"]:
            return True
    return False

async def restricted_access_check(update: Update, context: ContextTypes.DEFAULT_TYPE, function_name=""):
    """Проверяет доступ к функциям"""
    user = update.effective_user
    
    # Функции, доступные без комнаты
    allowed_without_room = [
        "start", "join_room_menu", "join_room", "room_help", 
        "back_menu", "admin_*", "mini_game_menu", "game_", "quiz_",
        "battle_", "gift_ideas_menu", "gift_", "profile", "wish_examples"
        "wish_cancel", "wish_start"  # 🔥 ДОБАВЬТЕ ЭТУ СТРОЧКУ
    ]
    
    # Если функция в списке разрешенных или пользователь админ
    if any(fn in function_name for fn in allowed_without_room) or is_admin(update):
        return True
    
    # Проверяем, находится ли пользователь в комнате
    if not is_user_in_room(user.id):
        if update.callback_query:
            await update.callback_query.answer(
                "❌ Для использования этой функции нужно присоединиться к комнате!\n"
                "Используйте кнопку 'Присоединиться к комнате' в меню.",
                show_alert=True
            )
        else:
            await update.message.reply_text(
                "❌ Для использования этой функции нужно присоединиться к комнате!\n"
                "Используйте кнопку 'Присоединиться к комнате' в меню."
            )
        return False
    return True
    
# -------------------------------------------------------------------
# 🎁 РАСШИРЕННЫЙ ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ
# -------------------------------------------------------------------

async def gift_ideas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await restricted_access_check(update, context, "gift_ideas_menu"):
        return
    
    await update.callback_query.answer()
    
    menu_text = """
🎁 <b>ГЕНЕРАТОР ИДЕЙ ПОДАРКОВ</b>

✨ <b>Выбери тип генерации:</b>

1. 🎯 <b>Базовая идея</b> - случайный подарок из 3 категорий
3. 🎪 <b>Идеи по тематике</b> - несколько идей по выбранной теме
4. 🔥 <b>Срочный подарок</b> - идеи для быстрой покупки
5. 🎨 <b>Готовые наборы</b> - комбинации подарков для разных случаев

💡 <b>Совет:</b> Чем точнее критерии, тем лучше будет результат!
"""
    
    keyboard = [
        [InlineKeyboardButton("🎯 Базовая идея", callback_data="gift_basic")],
        [InlineKeyboardButton("🎪 Идеи по тематике", callback_data="gift_themes_menu")],
        [InlineKeyboardButton("🔥 Срочный подарок", callback_data="gift_emergency_menu")],
        [InlineKeyboardButton("🎨 Готовые наборы", callback_data="gift_combinations")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        menu_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def gift_themes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    menu_text = """
🎪 <b>ИДЕИ ПО ТЕМАТИКЕ</b>

Выбери тематику для генерации идей:

🎭 <b>Доступные темы:</b>
• Романтический - для влюбленных
• Деловой - для коллег и партнеров
• Детский - для детей и подростков
• Эко - для любителей экологии
• Гастрономический - для ценителей вкуса
• Спортивный - для активных людей
• Творческий - для художников и мастеров
• Технический - для гиков и программистов
• Музыкальный - для музыкантов и меломаноз
• Путешествия - для исследователей мира

Каждая тема содержит 3 разные идеи!
"""
    
    keyboard = [
        [InlineKeyboardButton("❤️ Романтический", callback_data="gift_theme_romantic"),
         InlineKeyboardButton("💼 Деловой", callback_data="gift_theme_business")],
        [InlineKeyboardButton("👶 Детский", callback_data="gift_theme_kids"),
         InlineKeyboardButton("🌿 Эко", callback_data="gift_theme_eco")],
        [InlineKeyboardButton("🍽️ Гастрономический", callback_data="gift_theme_gastronomy"),
         InlineKeyboardButton("⚽ Спортивный", callback_data="gift_theme_sport")],
        [InlineKeyboardButton("🎨 Творческий", callback_data="gift_theme_creative"),
         InlineKeyboardButton("💻 Технический", callback_data="gift_theme_technical")],
        [InlineKeyboardButton("🎵 Музыкальный", callback_data="gift_theme_music"),
         InlineKeyboardButton("✈️ Путешествия", callback_data="gift_theme_travel")],
        [InlineKeyboardButton("🎲 Случайная тема", callback_data="gift_theme_random")],
        [InlineKeyboardButton("⬅️ Назад к идеям", callback_data="gift_ideas_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        menu_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def gift_emergency_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    menu_text = """
🔥 <b>СРОЧНЫЙ ПОДАРОК</b>

Нужен подарок срочно? Выбери параметры:

💰 <b>Бюджет:</b> До какой суммы?
⏰ <b>Срок:</b> Когда нужно успеть?

Идеи для покупки сегодня или с быстрой доставкой!
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 До 2000₽", callback_data="gift_emergency_2000")],
        [InlineKeyboardButton("💰 До 3000₽", callback_data="gift_emergency_3000")],
        [InlineKeyboardButton("💰 До 5000₽", callback_data="gift_emergency_5000")],
        [InlineKeyboardButton("⏰ На сегодня", callback_data="gift_emergency_today")],
        [InlineKeyboardButton("⏰ До завтра", callback_data="gift_emergency_tomorrow")],
        [InlineKeyboardButton("⏰ До недели", callback_data="gift_emergency_week")],
        [InlineKeyboardButton("🎲 Срочный подарок (случайный)", callback_data="gift_emergency_random")],
        [InlineKeyboardButton("⬅️ Назад к идеям", callback_data="gift_ideas_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        menu_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def generate_gift_idea():
    """Базовая функция генерации идеи подарка"""
    return generate_personalized_gift_idea()

def generate_personalized_gift_idea(recipient_type=None, occasion=None, max_price=None):
    """
    Генератор персонализированных идей подарков с фильтрами
    """
    
    # Расширенная база данных подарков
    EXPANDED_CATEGORIES = {
        "💻 Техника и гаджеты": {
            "items": [
                {"name": "Умная колонка с голосовым помощником", "price_range": "2000-5000", "recipient": "взрослый", "occasion": "любой"},
                {"name": "Беспроводные наушники с шумоподавлением", "price_range": "3000-15000", "recipient": "взрослый", "occasion": "любой"},
                {"name": "Портативная колонка для душа", "price_range": "1000-3000", "recipient": "взрослый", "occasion": "день рождения"},
            ],
            "description": "Современные устройства для комфорта и продуктивности"
        },
        
        "🎨 Творчество и хобби": {
            "items": [
                {"name": "Набор для каллиграфии с золотыми чернилами", "price_range": "2000-6000", "recipient": "творческий", "occasion": "любой"},
                {"name": "3D-ручка с цветными пластиками", "price_range": "1500-5000", "recipient": "ребенок", "occasion": "день рождения"},
                {"name": "Набор для вышивания портрета по фото", "price_range": "3000-8000", "recipient": "рукодельница", "occasion": "юбилей"},
            ],
            "description": "Для развития талантов и приятного времяпрепровождения"
        },
        
        "🏠 Уют и дом": {
            "items": [
                {"name": "Умный светильник с RGB подсветкой", "price_range": "2000-6000", "recipient": "молодежь", "occasion": "новоселье"},
                {"name": "Электрическая грелка в виде игрушки", "price_range": "1500-3500", "recipient": "женщина", "occasion": "холодный сезон"},
                {"name": "Набор ароматических свечей ручной работы", "price_range": "1000-4000", "recipient": "взрослый", "occasion": "рождество"},
            ],
            "description": "Вещи для создания атмосферы комфорта и тепла"
        },
        
        "👕 Мода и стиль": {
            "items": [
                {"name": "Кашемировый шарф с монограммой", "price_range": "3000-8000", "recipient": "стильный", "occasion": "зима"},
                {"name": "Кожаный ремень с гравировкой", "price_range": "2000-5000", "recipient": "мужчина", "occasion": "день рождения"},
                {"name": "Шелковый платок с ручной росписью", "price_range": "1500-4000", "recipient": "женщина", "occasion": "8 марта"},
            ],
            "description": "Аксессуары для завершения образа"
        },
        
        "📚 Образование и развитие": {
            "items": [
                {"name": "Подписка на онлайн-курс по интересам", "price_range": "2000-10000", "recipient": "студент", "occasion": "выпускной"},
                {"name": "Электронная книга с подпиской", "price_range": "5000-12000", "recipient": "читатель", "occasion": "день рождения"},
                {"name": "Настольная игра для развития логики", "price_range": "1500-4000", "recipient": "семья", "occasion": "вечер игр"},
            ],
            "description": "Инвестиции в знания и личностный рост"
        }
    }
    
    # Фильтрация по получателю
    recipient_filters = {
        "мужчина": ["мужчина", "взрослый", "стильный", "спортсмен", "путешественник", "друг", "гик", "кофеман", "кулинар"],
        "женщина": ["женщина", "взрослый", "стильный", "рукодельница", "зож", "гурман", "книголюб", "романтик"],
        "ребенок": ["ребенок", "начинающий", "молодежь", "студент"],
        "семья": ["семья", "взрослый", "друзья"],
        "любой": ["взрослый", "мужчина", "женщина", "ребенок", "семья", "пожилой", "друг", "коллеga"]
    }
    
    # Фильтрация по поводу
    occasion_filters = {
        "день рождения": ["день рождения", "любой", "юбилей", "отпуск", "выпускной"],
        "новый год": ["новый год", "рождество", "зима", "холодный сезон", "любой"],
        "8 марта": ["8 марта", "весна", "женский день", "любой"],
        "23 февраля": ["23 февраля", "мужской день", "любой"],
        "любой": ["любой", "день рождения", "новый год", "8 марта", "23 февраля", "годовщина", "новоселье"]
    }
    
    # Конвертация бюджета в числовой диапазон
    def parse_price_range(price_str):
        if "-" in price_str:
            min_p, max_p = price_str.split("-")
            return int(min_p), int(max_p)
        elif "от" in price_str:
            return int(price_str.replace("от", "").strip()), float('inf')
        elif "до" in price_str:
            return 0, int(price_str.replace("до", "").strip())
        return 0, float('inf')
    
    # Сбор всех подарков с учетом фильтров
    filtered_items = []
    
    for category_name, category_data in EXPANDED_CATEGORIES.items():
        for item in category_data["items"]:
            # Фильтр по получателю
            if recipient_type and recipient_type != "любой":
                if not any(r in item.get("recipient", "").lower() for r in recipient_filters.get(recipient_type, [])):
                    continue
            
            # Фильтр по поводу
            if occasion and occasion != "любой":
                if not any(o in item.get("occasion", "").lower() for o in occasion_filters.get(occasion, [])):
                    continue
            
            # Фильтр по цене
            if max_price:
                min_price, max_price_range = parse_price_range(item.get("price_range", "0-100000"))
                if max_price_range > max_price:
                    continue
            
            filtered_items.append((category_name, item, category_data["description"]))
    
    # Если нет подходящих подарков - возвращаем случайный
    if not filtered_items:
        category_name = random.choice(list(EXPANDED_CATEGORIES.keys()))
        item = random.choice(EXPANDED_CATEGORIES[category_name]["items"])
        description = EXPANDED_CATEGORIES[category_name]["description"]
    else:
        category_name, item, description = random.choice(filtered_items)
    
    # Генерация бюджета
    min_price, max_price_range = parse_price_range(item.get("price_range", "1000-5000"))
    avg_price = (min_price + max_price_range) / 2
    
    if avg_price < 2000:
        budget = "💰 Бюджет до 2000₽"
    elif avg_price < 5000:
        budget = "💸 Средний бюджет 2000-5000₽"
    elif avg_price < 10000:
        budget = "🎁 Премиум от 5000₽"
    else:
        budget = "💎 Люкс от 10000₽"
    
    # Формирование результата
    result = f"""
{category_name}
{'-'*40}
🎁 {item['name']}
💡 {description}
📊 Ориентировочная цена: {item.get('price_range', '1000-5000')}₽
{budget}
👤 Подходит для: {item.get('recipient', 'взрослого').title()}
🎉 Идеально для: {item.get('occasion', 'любого повода').title()}
    """
    
    return result


def gift_ideas_by_theme(theme, count=3):
    """Генератор нескольких идей по определенной тематике"""
    
    themes = {
        "романтический": ["мужчина", "женщина", "годовщина", "любовь"],
        "деловой": ["коллега", "взрослый", "босс", "партнер"],
        "детский": ["ребенок", "семья", "день рождения", "игрушки"],
        "эко": ["экоактивист", "взрослый", "садовод", "природа"],
        "гастрономический": ["гурман", "кулинар", "шеф", "встреча гостей"],
        "спортивный": ["спортсмен", "активный", "зож", "тренер"],
        "творческий": ["творческий", "художник", "рукодельница", "мастер"],
        "технический": ["технолюб", "программист", "гик", "инженер"],
        "музыкальный": ["музыкант", "меломан", "диджей", "певун"],
        "путешествия": ["путешественник", "турист", "исследователь", "отдых"]
    }
    
    if theme not in themes:
        theme = "любой"
    
    results = []
    for _ in range(count):
        if theme == "любой":
            result = generate_personalized_gift_idea()
        else:
            params = themes[theme]
            result = generate_personalized_gift_idea(
                recipient_type=random.choice(params) if random.random() > 0.5 else None,
                occasion=random.choice(params) if random.random() > 0.5 else None
            )
        results.append(result)
    
    return results


def emergency_gift_idea(budget_limit=2000, time_limit="сегодня"):
    """Идеи для срочного подарка"""
    
    urgent_gifts = [
        {"name": "Подарочная карта в любимый магазин", "category": "💳 Универсальное", "budget": "500-5000"},
        {"name": "Букет цветов с шоколадом", "category": "🌹 Романтика", "budget": "1000-3000"},
        {"name": "Книга-бестселлер с автографом", "category": "📚 Литература", "budget": "500-1500"},
        {"name": "Набор крафтового пива/чая", "category": "🍻 Для друга", "budget": "800-2000"},
    ]
    
    filtered = [g for g in urgent_gifts 
                if int(g["budget"].split("-")[0]) <= budget_limit]
    
    if not filtered:
        gift = random.choice(urgent_gifts)
    else:
        gift = random.choice(filtered)
    
    time_notes = {
        "сегодня": "🕐 Можно купить сегодня в магазинах рядом с вами",
        "завтра": "📦 Заказать с доставкой на завтра",
        "неделя": "📅 Есть время на поиск и заказ"
    }
    
    note = time_notes.get(time_limit, "⏰ Срочный подарок")
    
    return f"""
🚀 СРОЧНЫЙ ПОДАРОК ({time_limit.upper()})
{'-'*40}
{gift['category']}: {gift['name']}
💰 Бюджет: {gift['budget']}₽
{note}
💡 Совет: Добавьте открытку с теплыми словами!
    """


def get_gift_combinations():
    """Готовые комбинации подарков для разных ситуаций"""
    
    combinations = [
        {
            "name": "🎄 Новогодний набор",
            "items": ["Теплый плед", "Набор чая", "Книга для зимнего чтения", "Ароматическая свеча"],
            "total": "4000-8000₽",
            "occasion": "Новый год"
        },
        {
            "name": "🎂 День рождения друга",
            "items": ["Крутая футболка", "Настольная игра", "Бутылка хорошего вина", "Прикольные носки"],
            "total": "3000-6000₽",
            "occasion": "День рождения"
        }
    ]
    
    combo = random.choice(combinations)
    
    return f"""
🎁 ГОТОВЫЙ НАБОР ПОДАРКОВ
{'-'*40}
{combo['name']}
🎯 Для: {combo['occasion']}

📦 В набор входит:
{chr(10).join(f'   • {item}' for item in combo['items'])}

💰 Общий бюджет: {combo['total']}
💡 Идея: Все предметы можно красиво упаковать в одну коробку!
    """

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: ОСНОВНЫЕ КОМАНДЫ И ИНТЕРФЕЙС
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    admin = is_admin(update)
    init_user_data(user.id)
    
    data = load_all_data()
    
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
• Смотреть участников своей комнаты
• Получать идеи подарков
• Играть в квиз и битву с Гринчем

<b>💡 Подсказка:</b> Используй кнопки ниже для навигации
"""

    if is_admin(update):
        welcome_text += "\n\n⚙️ <b>Режим администратора активирован!</b>"
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not update.callback_query:
        await update.message.reply_text("Используйте кнопки в меню для этой команды.")
        return
    
    # 🔥 Сначала проверяем доступ к функции
    if not await restricted_access_check(update, context, "wish_start"):
        return
    
    await update.callback_query.answer()
    
    # 🔥 Проверяем, находится ли пользователь в комнате
    data = load_all_data()
    user = update.effective_user
    user_in_room = False
    
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            user_in_room = True
            break
    
    if not user_in_room:
        admin = is_admin(update)
        await update.callback_query.edit_message_text(
            "❌ Для написания пожелания нужно сначала присоединиться к комнате!\n"
            "Используй кнопку 'Присоединиться к комнате' в меню.",
            reply_markup=enhanced_menu_keyboard(admin)
        )
        return
    
    # Проверяем, не запущена ли уже игра
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            if room.get("game_started"):
                admin = is_admin(update)
                await update.callback_query.edit_message_text(
                    "🚫 Игра уже запущена! Менять пожелание нельзя.",
                    reply_markup=enhanced_menu_keyboard(admin)
                )
                return
    
    # Включаем режим ввода пожелания
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
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎁 Примеры пожеланий", callback_data="wish_examples")],
            [InlineKeyboardButton("❌ Отменить ввод", callback_data="wish_cancel")],
            [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
        ])
    )

async def wish_examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    examples = """
💡 <b>Примеры хороших пожеланий:</b>

🎨 <b>Для творческих:</b>
• "Хотел бы набор для рисования акварелью"
• "Интересна книга по фотографии"
• "Набор для создания украшений"

📚 <b>Для любителей чтения:</b>
• "Последняя книга любимого автора"
• "Красивое издание классики"
• "Подписка на аудиокниги"

☕ <b>Для ценителей уюта:</b>
• "Мягкий плед с новогодним принтом"
• "Набор ароматических свечей"
• "Красивая кружка для чая"

🎮 <b>Для геймеров:</b>
• "Игра, которую давно хотел попробовать"
• "Стикерпак для Telegram"
• "Аксессуар для компьютера"

<b>💡 Совет:</b> Чем конкретнее пожелание, тем проще Санте выбрать подарок!
"""
    
    await update.callback_query.edit_message_text(
        examples,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Написать пожелание", callback_data="wish")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
        ])
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # 🔥 Очищаем ВСЕ режимы при любом текстовом сообщении (кроме специальных случаев)
    if not context.user_data.get("wish_mode") and not context.user_data.get("join_mode"):
        context.user_data["wish_mode"] = False
        context.user_data["join_mode"] = False
        context.user_data["search_mode"] = False
    
    # 🔥 Пропускаем если это callback_query
    if update.callback_query:
        return
        
    data = load_all_data()
    user = update.effective_user
    admin = is_admin(update)
    
    # 🔥 УПРОЩЕННАЯ ПРОВЕРКА: Сначала смотрим, в каком режиме пользователь
    # Обработка пожелания
    if context.user_data.get("wish_mode"):
        # Проверяем, находится ли пользователь в комнате
        user_in_room = False
        for code, room in data["rooms"].items():
            if str(user.id) in room["members"]:
                user_in_room = True
                
                if room.get("game_started"):
                    await update.message.reply_text("🚫 Игра уже запущена! Менять пожелание нельзя.")
                    context.user_data["wish_mode"] = False
                    return
                
                room["members"][str(user.id)]["wish"] = update.message.text
                save_all_data(data)
                context.user_data["wish_mode"] = False
                
                await update.message.reply_text(
                    "✨ Пожелание сохранено! 🎄",
                    reply_markup=enhanced_menu_keyboard(admin)
                )
                return
        
        if not user_in_room:
            # Сбрасываем режим и показываем сообщение
            context.user_data["wish_mode"] = False
            await update.message.reply_text(
                "❌ Для написания пожелания нужно сначала присоединиться к комнате!\n"
                "Используй кнопку 'Присоединиться к комнате' в меню.",
                reply_markup=enhanced_menu_keyboard(admin)
            )
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

    # Обработка поиска пользователя (только для админа)
    if context.user_data.get("search_mode") and is_admin(update):
        await handle_search(update, context)
        return

    # Если ничего не подошло - показываем меню
    await update.message.reply_text(
        "Выбери действие в меню:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🏠 РАЗДЕЛ: УПРАВЛЕНИЕ КОМНАТАМИ
# -------------------------------------------------------------------
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        if update.callback_query:
            await update.callback_query.answer("🚫 Только @BeellyKid может создавать комнаты!", show_alert=True)
            return
        else:
            await update.message.reply_text("🚫 Только @BeellyKid может создавать комнаты.")
            return

    data = load_all_data()
    code = gen_room_code()
    data["rooms"][code] = {
        "creator": update.effective_user.id,
        "members": {},
        "game_started": False,
        "assign": {},
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    save_all_data(data)

    admin = is_admin(update)
    
    success_text = f"""
🎄 <b>Комната создана!</b>

<b>Код комнаты:</b> <code>{code}</code>
<b>Ссылка для приглашения:</b>
https://t.me/{(await context.bot.get_me()).username}?start=join_{code}

<b>💡 Инструкция:</b>
1. Отправь код комнаты друзьям
2. Они могут присоединиться через меню
3. После присоединения все пишут пожелания
4. Ты запускаешь игру кнопкой "Админ: Запуск игры"

<b>⚠️ Важно:</b> Минимум 2 участника для запуска игры!
"""
    
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
    # 🔥 Очищаем все режимы
    context.user_data["wish_mode"] = False
    context.user_data["join_mode"] = False
    context.user_data["search_mode"] = False
    
    if update.callback_query:
        await update.callback_query.answer()
    
    join_instructions = """
🎅 <b>Присоединение к комнате</b>

✨ <b>Как присоединиться:</b>
1. Попроси у организатора код комнаты (формат: RXXXXX)
2. Напиши код комнаты в чат с ботом

🔑 <b>Правила:</b>
• Можно быть только в одной комнате
• Присоединиться можно только до старта игры
• Минимум 2 участника для запуска
• Все участники должны написать пожелания

💡 <b>Подсказка:</b> Если у тебя есть код комнаты, просто напиши его ниже:
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            join_instructions,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Где взять код комнаты?", callback_data="room_help")],
                [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
            ])
        )
    else:
        await update.message.reply_text(
            join_instructions,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❓ Где взять код комнаты?", callback_data="room_help")],
                [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")]
            ])
        )
    
    # 🔥 Включаем режим присоединения
    context.user_data["join_mode"] = True

async def room_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    help_text = """
❓ <b>Где взять код комнаты?</b>

1. <b>У организатора:</b> Попроси у того, кто создавал игру
2. <b>В групповом чате:</b> Организатор мог отправить код в чат
3. <b>В личных сообщениях:</b> Проверь историю переписки с ботом

🔍 <b>Как выглядит код:</b> 6 символов, начинается с R
Пример: <code>RABC12</code>

💡 <b>Если нет кода:</b> 
• Создай свою комнату (если ты администратор)
• Или попроси друга создать комнату и прислать код
"""
    
    await update.callback_query.edit_message_text(
        help_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Ввести код комнаты", callback_data="join_room_menu")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
        ])
    )

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
        
    data = load_all_data()
    user = update.effective_user
    
    # Получаем код из сообщения
    if update.message.text.startswith('/join_room'):
        parts = update.message.text.split()
        code = parts[1].strip().upper() if len(parts) > 1 else None
    else:
        code = update.message.text.strip().upper()
    
    context.user_data["join_mode"] = False

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
        "wish": "",
        "joined_at": datetime.now(timezone.utc).isoformat()
    }
    save_all_data(data)

    admin = is_admin(update)
    await update.message.reply_text(
        f"✨ <b>Ты присоединился к комнате!</b> 🎄\n\n"
        f"<b>Код комнаты:</b> <code>{code}</code>\n"
        f"<b>Участников:</b> {len(room['members'])}\n"
        f"<b>Статус:</b> {'🟢 Игра активна' if room['game_started'] else '🟡 Ожидание запуска'}\n\n"
        f"<b>💡 Что делать дальше:</b>\n"
        f"1. Напиши своё пожелание через меню 🎁\n"
        f"2. Жди запуска игры организатором\n"
        f"3. После запуска получишь имя получателя!",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def show_room_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_all_data()
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
        await update.callback_query.answer("❌ Ты не в комнате! Присоединись к комнате через меню.", show_alert=True)
        return
    
    await show_specific_room_members(update, context, room_code, user_room)

async def admin_select_room_for_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_all_data()
    
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
        
    data = load_all_data()
    if not room:
        room = data["rooms"].get(code)
    
    if not room:
        await update.callback_query.answer("Комната не найдена!", show_alert=True)
        return
    
    members_text = f"👥 <b>Участники комнаты {code}:</b>\n\n"
    members_without_wish = []
    
    for i, (user_id, member) in enumerate(room["members"].items(), 1):
        wish_status = "✅" if member["wish"] else "❌"
        username = f"@{member['username']}" if member["username"] and member["username"] != "без username" else "без username"
        members_text += f"{i}. {member['name']} ({username}) {wish_status}\n"
        
        if not member["wish"]:
            members_without_wish.append(member['name'])
    
    members_text += f"\n<b>Всего участников:</b> {len(room['members'])}"
    members_text += f"\n<b>Статус игры:</b> {'✅ Запущена' if room['game_started'] else '⏳ Ожидание'}"
    
    if members_without_wish and not room["game_started"]:
        members_text += f"\n\n⚠️ <b>Без пожеланий:</b> {', '.join(members_without_wish)}"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]]
    
    if is_admin(update) and not room["game_started"] and len(room["members"]) >= 2:
        keyboard.insert(0, [InlineKeyboardButton("🚀 Запустить игру в этой комнате", callback_data=f"start_{code}")])
    
    await update.callback_query.edit_message_text(
        members_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------------------------------------------------------------------
# 🎮 РАЗДЕЛ: МИНИ-ИГРЫ (только квиз и битва с Гринчем)
# -------------------------------------------------------------------
async def mini_game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await restricted_access_check(update, context, "mini_game_menu"):
        return
    
    await update.callback_query.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    games_info = f"""
🎮 <b>Мини-игры</b>

✨ <b>Доступные игры:</b>

⚔️ <b>Битва с Гринчем</b> - Эпичная RPG-битва
• Сразись с Гринчем, который украл Рождество!
• Можно сбежать в любой момент
• Уникальные типы Гринчей
• Динамичная система боя

🎓 <b>Новогодний квиз</b> - Проверь знания
• 5 случайных вопросов
• Набирай очки за правильные ответы
• Смотри статистику в топе игроков
• Интересные факты!

Выбери игру:
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Битва с Гринчем", callback_data="game_grinch")],
        [InlineKeyboardButton("🎓 Новогодний квиз", callback_data="game_quiz")],
        [InlineKeyboardButton("📊 Топ игроков квиза", callback_data="quiz_top")],
        [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_menu")],
    ])
    await update.callback_query.edit_message_text(games_info, parse_mode='HTML', reply_markup=kb)

async def game_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "game_grinch":
        await game_grinch_handler(update, context)
        
    elif q.data == "game_quiz":
        await game_quiz_handler(update, context)
        
    elif q.data == "quiz_top":
        await show_quiz_top(update, context)
        
    elif q.data == "battle_start":
        await epic_grinch_battle(update, context)
        
    elif q.data == "quiz_start":
        await start_quiz(update, context)
        
    # СНАЧАЛА проверяем quiz_finish_now, потом другие quiz_
    elif q.data == "quiz_finish_now":
        await finish_quiz(update, context)
        
    elif q.data.startswith("battle_"):
        await battle_action_handler(update, context)
        
    elif q.data.startswith("quiz_"):
        if q.data == "quiz_next":
            await quiz_next_handler(update, context)
        elif q.data.startswith("quiz_answer_"):
            await quiz_answer_handler(update, context)
    
# Игра: Битва с Гринчем
async def game_grinch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    battle_info = """
⚔️ <b>Битва с Гринчем</b>

Гринч украл Рождество! Помоги Санте вернуть праздник.

<b>Правила битвы:</b>
• У тебя 100 HP
• У Гринча 120 HP
• Выбирай атаки и защиту
• Используй специальные умения
• Можно сбежать в любой момент

<b>💡 Советы:</b>
• Чередуй атаку и защиту
• Используй магию в критических ситуациях
• Не бойся отступать, если нужно

Готов сразиться?
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Начать битву!", callback_data="battle_start")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(battle_info, parse_mode='HTML', reply_markup=kb)

async def epic_grinch_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    user_data[str(user.id)]["grinch_fights"] = user_data[str(user.id)].get("grinch_fights", 0) + 1
    
    # Типы Гринча
    grinch_types = {
        "thief": {"name": "🎁 Вор подарков", "hp": 100, "attack": 25, "trait": "Может украсть предмет"},
        "berserk": {"name": "😠 Берсерк-Гринч", "hp": 140, "attack": 35, "trait": "Сильнее при низком HP"},
        "mage": {"name": "🧙 Маг-Гринч", "hp": 90, "attack": 28, "trait": "Использует магию"},
        "tank": {"name": "🛡️ Танк-Гринч", "hp": 180, "attack": 18, "trait": "Высокая защита"},
        "trickster": {"name": "🃏 Гринч-Трикстер", "hp": 110, "attack": 22, "trait": "Наводит помехи"}
    }
    
    grinch_type = random.choice(list(grinch_types.keys()))
    grinch_data = grinch_types[grinch_type]
    
    # Характеристики игрока
    player_stats = {
        "hp": 100,
        "max_hp": 100,
        "mana": 50,
        "max_mana": 50,
        "attack": random.randint(20, 30),
        "defense": random.randint(10, 18),
        "crit_chance": 0.15,
        "dodge_chance": 0.10,
        "special_charges": 3,
        "rage": 0,
        "items": {
            "potion": random.randint(1, 3),
            "bomb": random.randint(0, 2),
            "cookie": random.randint(0, 1)
        },
        "statuses": {
            "enchanted": 0,
            "shielded": 0,
            "bleeding": 0,
            "confused": 0
        }
    }
    
    # Характеристики Гринча
    grinch_stats = {
        "type": grinch_type,
        "name": grinch_data["name"],
        "hp": grinch_data["hp"],
        "max_hp": grinch_data["hp"],
        "attack": grinch_data["attack"],
        "defense": random.randint(12, 22),
        "special_used": False,
        "rage_mode": False,
        "phase": 1,
        "traits": grinch_data["trait"],
        "statuses": {},
        "abilities": {
            "steal": grinch_type == "thief",
            "magic": grinch_type == "mage",
            "heal": random.random() > 0.7,
            "summon": random.random() > 0.8
        }
    }
    
    # Создаем переменные среды
    environment = random.choice(["Снежная буря", "Замерзшая река", "Ёлочный лес", "Пещера Гринча", "Крыша города"])
    
    context.user_data["battle_state"] = {
        "player": player_stats,
        "grinch": grinch_stats,
        "round": 1,
        "environment": environment,
        "weather_effect": None,
        "battle_log": [
            f"⚔️ <b>Начинается эпичная битва с {grinch_stats['name']}!</b>",
            f"📍 <b>Место битвы:</b> {environment}",
            f"🎯 <b>Особенность Гринча:</b> {grinch_stats['traits']}",
            random.choice([
                "❄️ Гринч: 'Я украду Рождество, а потом и твой сэндвич!'",
                "🎁 Гринч: 'Подарки? Я делаю из них дрова для камина!'",
                "🦌 Гринч: 'Олени слишком медленные для моего побега на санях!'",
                "🍪 Гринч: 'Печенья для Санты? Я их уже съел. Извини!'"
            ])
        ],
        "combo": 0,
        "unexpected_events": []
    }
    
    await show_battle_interface(update, context)

async def show_battle_interface(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    # Визуализация HP
    def create_bar(current, max_val, filled="❤️", empty="♡", length=10):
        filled_count = int((current / max_val) * length)
        return filled * filled_count + empty * (length - filled_count)
    
    player_hp_bar = create_bar(player["hp"], player["max_hp"], "❤️", "♡")
    player_mana_bar = create_bar(player["mana"], player["max_mana"], "🔵", "⚫", 5)
    grinch_hp_bar = create_bar(grinch["hp"], grinch["max_hp"], "💚", "♡")
    
    # Отображение статусов
    status_effects = []
    for status, turns in player["statuses"].items():
        if turns > 0:
            status_icons = {
                "enchanted": "✨",
                "shielded": "🛡️",
                "bleeding": "🩸",
                "confused": "🌀"
            }
            status_effects.append(f"{status_icons.get(status, '❓')}{turns}")
    
    # Неожиданные события
    unexpected_text = ""
    if battle_state["unexpected_events"]:
        unexpected_text = "\n\n🎭 <b>Неожиданности:</b>\n" + "\n".join(battle_state["unexpected_events"][-2:])
    
    battle_text = f"""
⚔️ <b>БИТВА С ГРИНЧЕМ - Раунд {battle_state['round']}</b>
📍 <b>Место:</b> {battle_state['environment']}

🎅 <b>ТВОЙ САНТА:</b>
{player_hp_bar} {player['hp']}/{player['max_hp']} HP
{player_mana_bar} {player['mana']}/{player['max_mana']} Мана
⚡ Атака: {player['attack']} 🛡 Защита: {player['defense']}
🎒 Предметы: 🧪×{player['items']['potion']} 💣×{player['items']['bomb']} 🍪×{player['items']['cookie']}
{'📛 Статусы: ' + ' '.join(status_effects) if status_effects else ''}

🎄 <b>{grinch['name']}:</b>  
{grinch_hp_bar} {grinch['hp']}/{grinch['max_hp']} HP
{'😠 ФАЗА {grinch["phase"]}! ЯРОСТЬ!' if grinch['rage_mode'] else 'Фаза ' + str(grinch['phase'])}
⚡ Атака: {grinch['attack']} 🛡 Защита: {grinch['defense']}
🎯 Особость: {grinch['traits']}

<b>Выбери действие:</b>
{unexpected_text}
"""
    
    # Добавляем лог битвы если есть
    if battle_state["battle_log"]:
        battle_text += "\n\n📜 <b>Последние события:</b>\n" + "\n".join(battle_state['battle_log'][-3:]) + "\n"
    
    # Кнопки действий
    keyboard = [
        [InlineKeyboardButton("⚔️ Обычная атака", callback_data="battle_attack_normal"),
         InlineKeyboardButton("💥 Сильная атака (-10 маны)", callback_data="battle_attack_strong")],
        [InlineKeyboardButton("✨ Магическая атака (-20 маны)", callback_data="battle_attack_magic"),
         InlineKeyboardButton("🎯 Критический удар (-15 маны)", callback_data="battle_critical")],
        [InlineKeyboardButton("🛡️ Укрепить защиту (-10 маны)", callback_data="battle_defend"),
         InlineKeyboardButton("🌀 Запутать Гринча (-25 маны)", callback_data="battle_confuse")],
        [InlineKeyboardButton("🧪 Использовать зелье", callback_data="battle_item_potion"),
         InlineKeyboardButton("💣 Бросить бомбу", callback_data="battle_item_bomb")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="battle_flee")]
    ]
    
    await q.edit_message_text(battle_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def battle_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    action = q.data.replace("battle_", "")
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    battle_log = battle_state["battle_log"]
    result_text = ""
    
    # Обработка побега
    if action == "flee":
        flee_chance = random.random()
        flee_success = flee_chance > 0.4
        
        if flee_success:
            flee_messages = [
                "🏃 Ты успешно сбежал, оставив Гринча в недоумении!",
                "🚀 Используя реактивные сани, ты умчался прочь!",
                "🎅 Ты затерялся в снежной буре... но хотя бы живой!"
            ]
            result_text = random.choice(flee_messages)
            await show_battle_result(update, context, result_text)
            return
        else:
            flee_fail_messages = [
                "🚫 Гринч заблокировал выход гирляндой!",
                "🎄 Ты споткнулся о подарочную коробку!",
                "🦌 Олени отказались тебе помогать!"
            ]
            battle_log.append("🏃 " + random.choice(flee_fail_messages))
            # Гринч атакует за попытку побега
            damage = max(5, grinch["attack"] - player["defense"] // 4)
            player["hp"] -= damage
            battle_log.append(f"🎄 Гринч атаковал исподтишка! -{damage} HP")
    
    # Ход игрока
    elif action.startswith("attack_"):
        if "normal" in action:
            damage = calculate_damage(player, grinch, "normal")
            grinch["hp"] -= damage
            player["rage"] = min(100, player["rage"] + 10)
            crit = "💥 КРИТИЧЕСКИЙ УДАР! " if random.random() < player["crit_chance"] else ""
            battle_log.append(f"🎅 {crit}Ты атаковал! -{damage} HP Гринчу")
            
        elif "strong" in action:
            if player["mana"] >= 10:
                player["mana"] -= 10
                damage = calculate_damage(player, grinch, "strong")
                grinch["hp"] -= damage
                player["rage"] = min(100, player["rage"] + 15)
                battle_log.append(f"💥 Сильная атака! -{damage} HP Гринчу")
            else:
                battle_log.append("💢 Недостаточно маны! Атака провалилась")
                
        elif "magic" in action:
            if player["mana"] >= 20:
                player["mana"] -= 20
                damage = calculate_damage(player, grinch, "magic")
                grinch["hp"] -= damage
                if random.random() < 0.3:
                    grinch["defense"] = max(5, grinch["defense"] - 5)
                    battle_log.append(f"✨ Магия ослабила защиту Гринча! -{damage} HP")
                else:
                    battle_log.append(f"✨ Магическая атака! -{damage} HP Гринчу")
            else:
                battle_log.append("💢 Недостаточно маны для магии!")
    
    elif action == "critical":
        if player["mana"] >= 15:
            player["mana"] -= 15
            crit_damage = calculate_damage(player, grinch, "critical")
            grinch["hp"] -= crit_damage
            player["rage"] = min(100, player["rage"] + 20)
            critical_messages = [
                f"🎯 В яблочко! -{crit_damage} HP",
                f"💫 Прямо в нос Гринча! -{crit_damage} HP",
                f"🎄 Попал подарком по голове! -{crit_damage} HP"
            ]
            battle_log.append(random.choice(critical_messages))
        else:
            battle_log.append("💢 Нужно больше маны для критического удара!")
    
    elif action == "defend":
        if player["mana"] >= 10:
            player["mana"] -= 10
            defense_bonus = random.randint(8, 15)
            player["defense"] += defense_bonus
            player["statuses"]["shielded"] = 2
            battle_log.append(f"🛡️ Защита усилена! +{defense_bonus} к защите на 2 хода")
        else:
            battle_log.append("💢 Недостаточно маны для защиты!")
    
    elif action == "confuse":
        if player["mana"] >= 25:
            player["mana"] -= 25
            grinch["statuses"]["confused"] = 3
            confuse_messages = [
                "🌀 Гринч запутался в гирляндах!",
                "🎁 Ты показал блестящую игрушку - Гринч дезориентирован!",
                "✨ Магия замешательства подействовала!"
            ]
            battle_log.append(random.choice(confuse_messages))
        else:
            battle_log.append("💢 Недостаточно маны для замешательства!")
    
    elif action.startswith("item_"):
        item_type = action.replace("item_", "")
        
        if item_type == "potion" and player["items"]["potion"] > 0:
            player["items"]["potion"] -= 1
            heal = random.randint(30, 50)
            player["hp"] = min(player["max_hp"], player["hp"] + heal)
            potion_messages = [
                f"🧪 Выпил зелье! +{heal} HP",
                f"💊 Проглотил волшебную микстуру! +{heal} HP",
                f"🥤 Новогодний эликсир восстановил {heal} HP"
            ]
            battle_log.append(random.choice(potion_messages))
            
        elif item_type == "bomb" and player["items"]["bomb"] > 0:
            player["items"]["bomb"] -= 1
            damage = random.randint(25, 40)
            grinch["hp"] -= damage
            bomb_messages = [
                f"💣 Бомба из конфетти! -{damage} HP",
                f"🎆 Фейерверк в лицо Гринчу! -{damage} HP",
                f"🧨 Подарочная бомба взорвалась! -{damage} HP"
            ]
            battle_log.append(random.choice(bomb_messages))
            
        elif item_type == "cookie" and player["items"]["cookie"] > 0:
            player["items"]["cookie"] -= 1
            player["hp"] = player["max_hp"]
            player["mana"] = player["max_mana"]
            battle_log.append("🍪 Волшебное печенье восстановило всё здоровье и ману!")
    
    # Проверка статусов игрока
    process_player_statuses(player, battle_log)
    
    # Проверка победы
    if grinch["hp"] <= 0:
        await battle_victory(update, context, battle_log)
        return
    
    # Ход Гринча
    if grinch["hp"] > 0:
        await grinch_turn(update, context, battle_log)
    
    # Проверка поражения
    if player["hp"] <= 0:
        await battle_defeat(update, context, battle_log)
        return
    
    # Восстановление маны
    player["mana"] = min(player["max_mana"], player["mana"] + 5)
    
    # Шанс на неожиданное событие
    if random.random() < 0.25:
        trigger_unexpected_event(battle_state)
    
    # Увеличение раунда
    battle_state["round"] += 1
    
    # Смена фаз Гринча
    if grinch["hp"] < grinch["max_hp"] * 0.3 and grinch["phase"] == 1:
        grinch["phase"] = 2
        grinch["rage_mode"] = True
        grinch["attack"] += 15
        battle_log.append("😠 ГРИНЧ ВПАЛ В ЯРОСТЬ! Его атака резко возросла!")
        
    elif grinch["hp"] < grinch["max_hp"] * 0.15 and grinch["phase"] == 2:
        grinch["phase"] = 3
        desperate_moves = [
            "💢 'Я не сдамся так легко!'",
            "🎄 'Заберу тебя с собой в небытие!'",
            "🦌 'Даже олени не спасут тебя теперь!'"
        ]
        battle_log.append(random.choice(desperate_moves))
        grinch["hp"] += 20
        battle_log.append("💚 Гринч собрал последние силы! +20 HP")
    
    battle_state["battle_log"] = battle_log[-5:]
    
    await show_battle_interface(update, context)

async def grinch_turn(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    battle_state = context.user_data["battle_state"]
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    # Шанс уклонения игрока
    if random.random() < player["dodge_chance"]:
        dodge_messages = [
            "🎅 Ловко увернулся от атаки!",
            "🦌 Олень оттащил тебя в сторону!",
            "❄️ Снежная туча скрыла тебя!"
        ]
        battle_log.append(random.choice(dodge_messages))
        return
    
    # Эффект замешательства
    if grinch.get("statuses", {}).get("confused", 0) > 0:
        if random.random() < 0.5:
            battle_log.append("🌀 Гринч слишком смущён и пропускает ход!")
            grinch["statuses"]["confused"] -= 1
            return
    
    # Выбор атаки Гринча
    if grinch["type"] == "thief" and random.random() > 0.7:
        if player["items"]["potion"] > 0:
            player["items"]["potion"] -= 1
            grinch["hp"] += 15
            battle_log.append("🎁 Гринч украл твоё зелье и выпил его! +15 HP Гринчу")
            return
    
    grinch_attacks = []
    
    if grinch["type"] == "berserk" and grinch["hp"] < grinch["max_hp"] * 0.4:
        grinch_attacks.append(("💢 Безумная ярость!", "strong"))
        grinch_attacks.append(("💢 Безумная ярость!", "strong"))
    
    elif grinch["type"] == "mage":
        grinch_attacks.append(("✨ Тёмная магия!", "magic"))
        grinch_attacks.append(("🌀 Магический вихрь!", "magic"))
    
    elif grinch["type"] == "tank":
        grinch_attacks.append(("🛡️ Тяжёлый удар!", "strong"))
        grinch_attacks.append(("💥 Сокрушительный удар!", "strong"))
    
    else:
        grinch_attacks.append(("🎄 Атака подарочной коробкой!", "normal"))
        grinch_attacks.append(("🦌 Удар оленьими рогами!", "normal"))
        grinch_attacks.append(("🍪 Бросок твёрдым печеньем!", "normal"))
    
    # Добавляем особые атаки
    special_attacks = [
        ("🎶 Пронзительное пение!", "magic", 0.1),
        ("🎁 Взрыв конфетти!", "aoe", 0.15),
        ("🦌 Призыв оленей-зомби!", "summon", 0.08),
        ("🎄 Ёлка-метательный снаряд!", "strong", 0.2)
    ]
    
    for attack_name, attack_type, chance in special_attacks:
        if random.random() < chance:
            grinch_attacks.append((attack_name, attack_type))
            break
    
    # Выбираем случайную атаку
    attack_name, attack_type = random.choice(grinch_attacks)
    
    # Расчёт урона
    base_damage = grinch["attack"]
    if attack_type == "strong":
        base_damage = int(base_damage * 1.5)
    elif attack_type == "magic":
        base_damage = int(base_damage * 1.3)
        if random.random() < 0.25:
            player["statuses"]["bleeding"] = 2
            battle_log.append("🩸 Ты истекаешь кровью!")
    
    damage = max(5, base_damage - player["defense"] // 3)
    
    if grinch["rage_mode"]:
        damage = int(damage * 1.3)
    
    player["hp"] -= damage
    battle_log.append(f"🎄 {attack_name} -{damage} HP")
    
    if "summon" in attack_type:
        extra_damage = random.randint(5, 15)
        player["hp"] -= extra_damage
        summon_messages = [
            f"🦌 Олени-зомби атакуют! -{extra_damage} HP",
            f"🎅 Призраки прошлых Гринчей помогают! -{extra_damage} HP"
        ]
        battle_log.append(random.choice(summon_messages))
    
    elif "aoe" in attack_type:
        if player.get("statuses", {}).get("shielded", 0) > 0:
            reduced_damage = max(1, damage // 2)
            player["hp"] += damage - reduced_damage
            battle_log.append(f"🛡️ Щит поглотил часть урона! Осталось -{reduced_damage} HP")

def trigger_unexpected_event(battle_state):
    events = [
        ("🎅 Внезапно появился эльф и подкинул зелье!", 
         lambda p, g: p["items"].update({"potion": p["items"]["potion"] + 1})),
        
        ("🦌 Пролетающий олень сбросил подарок!", 
         lambda p, g: p["hp"] + 10 if p["hp"] < p["max_hp"] else None),
        
        ("🍪 С неба упало волшебное печенье!", 
         lambda p, g: p["items"].update({"cookie": p["items"]["cookie"] + 1})),
        
        ("🎁 Один из украденных подарков взорвался!", 
         lambda p, g: g["hp"] - random.randint(10, 20)),
    ]
    
    event_text, effect = random.choice(events)
    battle_state["unexpected_events"].append(event_text)
    
    player = battle_state["player"]
    grinch = battle_state["grinch"]
    
    result = effect(player, grinch)
    if result:
        if isinstance(result, tuple):
            for res in result:
                if isinstance(res, int):
                    if res > 0:
                        player["hp"] = min(player["max_hp"], player["hp"] + res)
                    elif res < 0:
                        grinch["hp"] -= abs(res)
        elif isinstance(result, int):
            if result > 0:
                player["hp"] = min(player["max_hp"], player["hp"] + result)
            else:
                grinch["hp"] -= abs(result)

def process_player_statuses(player, battle_log):
    for status in list(player["statuses"].keys()):
        if player["statuses"][status] > 0:
            player["statuses"][status] -= 1
    
    if player.get("statuses", {}).get("bleeding", 0) > 0:
        bleed_damage = random.randint(3, 8)
        player["hp"] -= bleed_damage
        bleed_messages = [
            f"🩸 Кровотечение! -{bleed_damage} HP",
            f"💧 Теряешь кровь! -{bleed_damage} HP"
        ]
        battle_log.append(random.choice(bleed_messages))
    
    if player.get("statuses", {}).get("enchanted", 0) > 0:
        player["attack"] += 5
    
    if player.get("statuses", {}).get("shielded", 0) == 0 and player["defense"] > 15:
        player["defense"] = max(15, player["defense"] - 5)
        battle_log.append("🛡️ Защита ослабла")

def calculate_damage(player, grinch, attack_type):
    base_damage = player["attack"]
    
    if attack_type == "normal":
        damage = base_damage + random.randint(-3, 5)
    elif attack_type == "strong":
        damage = int(base_damage * 1.5) + random.randint(0, 8)
    elif attack_type == "magic":
        damage = int(base_damage * 1.3) + random.randint(2, 10)
    elif attack_type == "critical":
        damage = int(base_damage * 2.0) + random.randint(5, 15)
    
    damage = max(5, damage - grinch["defense"] // 4)
    
    if player.get("statuses", {}).get("enchanted", 0) > 0:
        damage = int(damage * 1.2)
    
    return damage

async def battle_victory(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    user = update.effective_user
    user_data[str(user.id)]["grinch_wins"] = user_data[str(user.id)].get("grinch_wins", 0) + 1
    user_data[str(user.id)]["games_won"] = user_data[str(user.id)].get("games_won", 0) + 1
    
    grinch_type = context.user_data["battle_state"]["grinch"]["type"]
    type_names = {
        "thief": "Воpa подарков",
        "berserk": "Берсерка",
        "mage": "Мага",
        "tank": "Танка",
        "trickster": "Трикстера"
    }
    
    victory_messages = [
        f"🎉 <b>ПОБЕДА НАД {type_names.get(grinch_type, 'Гринчем').upper()}!</b> 🎉",
        f"✨ <b>Гринч повержен! Рождество спасено!</b> ✨",
        f"🏆 <b>Триумф! Гринч побеждён!</b> 🏆"
    ]
    
    round_count = context.user_data["battle_state"]["round"]
    combo = context.user_data["battle_state"].get("combo", 0)
    
    victory_text = f"""
{random.choice(victory_messages)}

📊 <b>Статистика битвы:</b>
• Пройдено раундов: {round_count}
• Максимальное комбо: {combo}
• Оставшееся HP: {context.user_data['battle_state']['player']['hp']}
• Использовано предметов: {3 - sum(context.user_data['battle_state']['player']['items'].values())}

Поздравляю с победой! 🎄
"""
        
    keyboard = [
        [InlineKeyboardButton("🎮 Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(victory_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    
async def battle_defeat(update: Update, context: ContextTypes.DEFAULT_TYPE, battle_log):
    defeat_text = f"""
💔 <b>ПОРАЖЕНИЕ...</b>

📜 <b>Ход битвы:</b>
""" + "\n".join(battle_log[-5:]) + f"""

Не сдавайся! Гринч должен быть остановлен! 🎅
"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Попробовать снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(defeat_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def show_battle_result(update: Update, context: ContextTypes.DEFAULT_TYPE, result_text):
    keyboard = [
        [InlineKeyboardButton("🎮 Сразиться снова", callback_data="game_grinch")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        result_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -------------------------------------------------------------------
# 🎓 НОВОГОДНИЙ КВИЗ
# -------------------------------------------------------------------
NEW_YEAR_QUIZ = [
{"id": 1, "question": "🎄 В какой стране начали наряжать ёлку на Новый год?", "options": ["🇩🇪 Германия", "🇷🇺 Россия", "🇺🇸 США", "🇫🇷 Франция"], "correct": 0, "fact": "Традиция наряжать ёлку зародилась в Германии в XVI веке!"},
{"id": 2, "question": "⭐ Сколько лучей у снежинки?", "options": ["4", "6", "8", "10"], "correct": 1, "fact": "Правильно! У снежинки всегда 6 лучей из-за кристаллической структуры льда."},
{"id": 3, "question": "🎅 Как зовут оленя с красным носом?", "options": ["Рудольф", "Дашер", "Дансер", "Комет"], "correct": 0, "fact": "Рудольф — самый известный олень Санты с красным светящимся носом!"},
{"id": 4, "question": "🕛 Во сколько бьют куранты в новогоднюю ночь?", "options": ["23:55", "00:00", "00:05", "00:10"], "correct": 1, "fact": "Куранты бьют ровно в полночь, символизируя наступление Нового года!"},
{"id": 5, "question": "🍪 Кто обычно оставляет подарки под ёлкой в России?", "options": ["Санта Клаус", "Дед Мороз", "Снегурочка", "Йоулупукки"], "correct": 1, "fact": "В России подарки под ёлкой оставляет Дед Мороз со своей внучкой Снегурочкой!"},
{"id": 6, "question": "📺 Что традиционно показывают по ТВ в России перед бойом курантов 31 декабря?", "options": ["«Карнавальная ночь»", "«Ирония судьбы»", "«Джентльмены удачи»", "«Голубой огонёк»"], "correct": 1, "fact": "«Ирония судьбы, или С лёгким паром!» — самая популярная новогодняя комедия, которую показывают уже несколько десятилетий!"},
{"id": 7, "question": "🥂 С каким напитком в России часто связывают новогоднее застолье?", "options": ["Советское шампанское", "Английский эль", "Немецкий глинтвейн", "Французский коньяк"], "correct": 0, "fact": "«Советское шампанское» стало неизменным атрибутом новогоднего стола с 60-х годов XX века."},
{"id": 8, "question": "🧦 Где в доме в англоязычных странах вешают носок для подарков?", "options": ["На дверную ручку", "На камин", "Под ёлку", "У кровати"], "correct": 1, "fact": "По легенде, Санта однажды обронил монеты в дымоход, и они попали в носок, сушившийся у камина. С тех пор носки вешают именно там!"},
{"id": 9, "question": "🎁 Что принято дарить на китайский Новый год?", "options": ["Красные конверты с деньгами", "Золотые украшения", "Корзины с фруктами", "Свечи"], "correct": 0, "fact": "«Хунбао» — красные конверты с деньгами — дарят детям и молодым родственникам на удачу."},
{"id": 10, "question": "🎆 В какой стране на Новый год запускают огромный фейерверк над гаванью Сиднея?", "options": ["🇦🇺 Австралия", "🇯🇵 Япония", "🇨🇳 Китай", "🇳🇿 Новая Зеландия"], "correct": 0, "fact": "Сиднейский фейерверк — один из первых масштабных салютов в мире из-за разницы во времени!"},
{"id": 11, "question": "🎵 Как называется самая известная новогодняя песня, начинающаяся со слов «Jingle bells, jingle bells…»?", "options": ["«We Wish You a Merry Christmas»", "«Jingle Bells»", "«Silent Night»", "«Let It Snow»"], "correct": 1, "fact": "Интересно, что «Jingle Bells» изначально была написана для Дня Благодарения, а не для Рождества!"},
{"id": 12, "question": "🧑‍🎄 Как зовут рождественского эльфа-помощника Санты, который известен своими шутками?", "options": ["Базиль", "Элвис", "Динки-Ду", "Патч"], "correct": 3, "fact": "Эльф по имени Патч (или Элфи) — один из самых известных помощников, часто попадающий в смешные истории в мультфильмах."},
{"id": 13, "question": "🍗 Что традиционно готовят на рождественский ужин в Англии?", "options": ["Жареного гуся", "Запечённую индейку", "Рождественский пудинг", "Фаршированную свинину"], "correct": 1, "fact": "Хотя раньше популярен был гусь, сейчас главное блюдо английского Рождества — запечённая индейка с начинкой!"},
{"id": 14, "question": "⛪ Когда православные христиане празднуют Рождество?", "options": ["24 декабря", "25 декабря", "6 января", "7 января"], "correct": 3, "fact": "Православное Рождество отмечается 7 января из-за разницы между Григорианским и Юлианским календарями."},
{"id": 15, "question": "🥟 Что принято лепить на Новый год в России, спрятав в один из кусочков монетку?", "options": ["Вареники", "Пельмени", "Блины", "Оладьи"], "correct": 0, "fact": "Вареники с сюрпризом (монетка, фасоль, перец) — старая славянская традиция на праздник: кому что попадётся, того и ждёт в новом году."},
{"id": 16, "question": "🎬 В каком фильме звучит фраза «С Новым годом, Шура!»?", "options": ["«Бриллиантовая рука»", "«Операция «Ы»»", "«Кавказская пленница»", "«Иван Васильевич меняет профессию»"], "correct": 3, "fact": "Эта знаменитая фраза — из фильма «Иван Васильевич меняет профессию», где её произносит царь Иван Грозный (Юрий Яковлев)."},
{"id": 17, "question": "🕯️ Какой праздник отмечают 6 января в некоторых странах, завершая период рождественских праздников?", "options": ["День трёх королей", "Канун Нового года", "День святого Николая", "Сочельник"], "correct": 0, "fact": "День трёх королей (Богоявление) символизирует приход волхвов к младенцу Иисусу. В этот день часто пишут мелом на дверях инициалы королей: K+M+B."},
{"id": 18, "question": "🥂 Что делают с бокалом шампанского, когда бьют куранты?", "options": ["Разбивают об пол", "Выпивают до дна", "Загадывают желание и чокаются", "Ставят на стол и не трогают"], "correct": 2, "fact": "Считается, что если успеть загадать желание, пока бьют 12 курантов, и выпить шампанское, то оно сбудется."},
{"id": 19, "question": "🐭 Кто, согласно восточному календарю, был первым животным в 12-летнем цикле?", "options": ["Бык", "Крыса", "Тигр", "Дракон"], "correct": 1, "fact": "По легенде, Будда позвал животных, и первой прибежала Крыса, проехавшись на спине Быка и спрыгнув прямо перед финишем!"},
{"id": 20, "question": "🎪 Где находится официальная резиденция российского Деда Мороза?", "options": ["Москва", "Суздаль", "Великий Устюг", "Ярославль"], "correct": 2, "fact": "С 1999 года вотчиной Деда Мороза официально считается город Великий Устюг в Вологодской области."},
{"id": 21, "question": "🇫🇮 Как зовут финского «коллегу» Деда Мороза?", "options": ["Пер Ноэль", "Йоулупукки", "Синтерклаас", "Папа Ноэль"], "correct": 1, "fact": "Йоулупукки (в переводе «рождественский козёл») живёт в Лапландии, на горе Корватунтури."},
{"id": 22, "question": "🍬 Как называется красно-белая леденцовая палочка, популярная на Рождество?", "options": ["Канди-кейн", "Лолипоп", "Барбарис", "Мятная трость"], "correct": 0, "fact": "Леденец «Candy Cane» по форме напоминает пастуший посох, что символизирует Иисуса как доброго пастыря."},
{"id": 23, "question": "❄️ Какой фильм с участием Арнольда Шварценеггера стал культовым на Новый год?", "options": ["«Терминатор»", "«Коммандо»", "«Правдивая ложь»", "«Один дома 2» (камео)"], "correct": 3, "fact": "В фильме «Один дома 2: Потерявшийся в Нью-Йорке» Арнольд появляется в роли самого себя, а его фраза «Put that cookie down!» стала мемом."},
{"id": 24, "question": "📜 Что принято писать в новогодних открытках чаще всего?", "options": ["Поздравления в стихах", "Список подарков", "Пожелания здоровья и счастья", "Отчёт о прошедшем годе"], "correct": 2, "fact": "Самые частые пожелания — здоровья, счастья, благополучия и успехов в новом году."},
{"id": 25, "question": "🌠 Как называется ночь с 31 декабря на 1 января?", "options": ["Ночь чудес", "Старый Новый год", "Канун Нового года", "Ночь желаний"], "correct": 2, "fact": "Канун Нового года (New Year's Eve) — время прощания с уходящим годом и встречи нового."},
{"id": 26, "question": "🥮 Что принято готовить на Новый год в Италии?", "options": ["Панеттоне", "Пастила", "Тирамису", "Пицца"], "correct": 0, "fact": "Панеттоне — высокий сладкий пирог с цукатами, без которого не обходится ни одно итальянское Рождество и Новый год."},
{"id": 27, "question": "👘 В какой стране на Новый год надевают традиционные кимоно и посещают храмы?", "options": ["🇰🇷 Корея", "🇯🇵 Япония", "🇻🇳 Вьетнам", "🇹🇭 Таиланд"], "correct": 1, "fact": "В Японии Новый год (О-сёгацу) — очень важный праздник. Люди надевают кимоно, едят особую лапшу тосикоси и слушают 108 ударов храмового колокола."},
{"id": 28, "question": "🔥 Что сжигают в некоторых странах Латинской Америки на Новый год?", "options": ["Старые вещи", "Чучело старого года", "Ёлку", "Фейерверки"], "correct": 1, "fact": "В Мексике, Колумбии и других странах делают чучело (Año Viejo), символизирующее уходящий год, и сжигают его в полночь."},
{"id": 29, "question": "🧹 Куда, по примете, нужно выбросить мусор до наступления Нового года?", "options": ["В окно", "Из дома", "В соседский двор", "Его нельзя выносить вообще"], "correct": 1, "fact": "Считается, что если вынести мусор после наступления Нового года, то вместе с ним вынесешь и благополучие."},
{"id": 30, "question": "🎇 Какой город известен самым масштабным новогодним салютом в мире?", "options": ["Нью-Йорк (Таймс-сквер)", "Лондон (Лондонский глаз)", "Дубай (Бурдж-Халифа)", "Сидней (Сиднейская гавань)"], "correct": 2, "fact": "Фейерверк у небоскрёба Бурдж-Халифа в Дубае — один из самых дорогих и технически сложных в мире."},
{"id": 31, "question": "🎭 Кто такая Снегурочка по отношению к Деду Морозу?", "options": ["Жена", "Дочь", "Внучка", "Сестра"], "correct": 2, "fact": "Снегурочка — уникальный для России сказочный персонаж, внучка Деда Мороза. У западного Санты такого помощника нет."},
{"id": 32, "question": "🍇 Что съедают в Испании под каждый удар курантов в новогоднюю ночь?", "options": ["Виноградины", "Оливки", "Кусочки сыра", "Миндальные орехи"], "correct": 0, "fact": "Традиция «12 виноградин удачи»: нужно успеть съесть по ягодке под каждый из 12 ударов, тогда год будет удачным."},
{"id": 33, "question": "🐖 Какое животное, согласно примете, должно первым переступить порог дома в Новом году для удачи?", "options": ["Чёрная кошка", "Светлый мужчина", "Маленький ребёнок", "Рыжий пёс"], "correct": 1, "fact": "Старая славянская примета: если первым в новом году в дом войдёт мужчина (особенно с тёмными волосами), это к благополучию."},
{"id": 34, "question": "🕰️ Какой праздник отмечают в ночь с 13 на 14 января в России и некоторых соседних странах?", "options": ["Международный день спасибо", "Старый Новый год", "Рождественский сочельник", "Крещение"], "correct": 1, "fact": "Старый Новый год — это Новый год по Юлианскому календарю. Праздник-«анахронизм», сохранившийся из-за разницы в календарях."},
{"id": 35, "question": "🎶 Какой композитор написал знаменитый балет «Щелкунчик»?", "options": ["Чайковский", "Прокофьев", "Моцарт", "Штраус"], "correct": 0, "fact": "Балет Петра Ильича Чайковского «Щелкунчик» на сюжет Гофмана — неотъемлемая часть рождественских и новогодних традиций во всём мире."},
{"id": 36, "question": "🧧 Какого цвета обычно конверты для денежных подарков на китайский Новый год?", "options": ["Зелёного", "Красного", "Золотого", "Белого"], "correct": 1, "fact": "Красный цвет в Китае символизирует удачу, счастье и prosperity, поэтому все подарки и украшения — красные."},
{"id": 37, "question": "🦃 В какой стране на Новый год готовят «Жареного цыплёнка по-столичному»?", "options": ["🇺🇸 США", "🇬🇧 Великобритания", "🇷🇺 Россия", "🇯🇵 Япония"], "correct": 2, "fact": "Салат «Оливье», который на Западе называют «Russian salad», в СССР часто именовали «Столичным», а его главным ингредиентом был рябчик или курица."},
{"id": 38, "question": "🎬 Какой фильм начинается со слов «Представьте, что вы король…» и является новогодней классикой?", "options": ["«Ирония судьбы»", "«Карнавальная ночь»", "«Чародеи»", "«Джентельмены удачи»"], "correct": 2, "fact": "Фильм «Чародеи» по пьесе братьев Стругацких традиционно показывают в новогодние праздники. Цитата «Счастье — это когда тебя понимают» тоже оттуда!"},
{"id": 39, "question": "⛄ Из чего дети обычно лепят снеговика?", "options": ["Двух снежных шаров", "Трёх снежных шаров", "Четырёх снежных шаров", "Одного большого кома"], "correct": 1, "fact": "Классический снеговик состоит из трёх комов разного размера: большой (живот), средний (грудь) и маленький (голова)."},
{"id": 40, "question": "🍊 Что кладут в рождественский чулок в Англии, кроме подарков, согласно старой традиции?", "options": ["Апельсин", "Ломтик пирога", "Уголёк", "Монетку"], "correct": 0, "fact": "Апельсин в носке символизирует золотой мешок, который, по легенде, Святой Николай (прообраз Санты) подарил бедной семье."},
{"id": 41, "question": "🎄 Что было первым рождественским деревом, которое начали наряжать?", "options": ["Ель", "Сосна", "Пихта", "Дуб"], "correct": 0, "fact": "Именно ель, вечнозелёное дерево, считалось у древних германцев символом жизни и плодородия зимой."},
{"id": 42, "question": "✉️ Кому дети в разных странах пишут письма перед Рождеством и Новым годом?", "options": ["Родителям", "Деду Морозу/Санта Клаусу", "Президенту", "Главному волшебнику"], "correct": 1, "fact": "Письма с пожеланиями подарков отправляются на «Северный полюс» или на специальные почтовые адреса, которые существуют во многих странах."},
{"id": 43, "question": "🎁 Что дарят на Рождество в Швеции, следуя традиции «Рождественского козла»?", "options": ["Соломенные фигурки", "Козье молоко", "Шерстяные носки", "Сладости в форме козлика"], "correct": 0, "fact": "Йольский козёл — древний скандинавский символ. Сейчас дарят маленькие соломенные фигурки козликов как талисманы."},
{"id": 44, "question": "🕯️ Как называется день перед Рождеством (24 декабря)?", "options": ["Канун Рождества", "Рождественский вечер", "Сочельник", "Все варианты верны"], "correct": 3, "fact": "Все эти названия верны! В этот день заканчивается строгий пост у христиан и начинаются праздничные богослужения."},
{"id": 45, "question": "🥂 Что кричат в новогоднюю ночь вместо «Ура!» в англоязычных странах?", "options": ["Merry Christmas!", "Happy New Year!", "Cheers!", "Auld Lang Syne!"], "correct": 1, "fact": "Фраза «Happy New Year!» — самое популярное поздравление. Также часто поют песню «Auld Lang Syne»."},
{"id": 46, "question": "🎬 Какой советский фильм стал первым, действие которого происходит именно в новогоднюю ночь?", "options": ["«В бой идут одни «старики»»", "«Карнавальная ночь»", "«Москва слезам не верит»", "«Служебный роман»"], "correct": 1, "fact": "«Карнавальная ночь» (1956) Эльдара Рязанова — первая советская новогодняя комедия, подарившая нам «Песенку о хорошем настроении»."},
{"id": 47, "question": "🇬🇧 Где в Лондоне собираются толпы людей, чтобы встретить Новый год?", "options": ["На Трафальгарской площади", "У Биг-Бена", "У Лондонского глаза", "В Гайд-парке"], "correct": 2, "fact": "Сотни тысяч людей собираются на набережной Темзы, чтобы увидеть фейерверк вокруг колеса обозрения «Лондонский глаз»."},
{"id": 48, "question": "🥮 Как называется традиционный немецкий рождественский кекс с цукатами и орехами?", "options": ["Штоллен", "Лебкухен", "Брауни", "Фондан"], "correct": 0, "fact": "Штоллен (или Дрезденский штоллен) выпекают за несколько недель до Рождества и обильно посыпают сахарной пудрой, символизирующей пелёнки младенца Иисуса."},
{"id": 49, "question": "🦌 Как зовут оленя, который возглавляет упряжку Санты в известной песне?", "options": ["Рудольф", "Дашер", "Дансер", "Блитцен"], "correct": 1, "fact": "В песне «Rudolph the Red-Nosed Reindeer» перечисляются все 8 оленей: Dasher, Dancer, Prancer, Vixen, Comet, Cupid, Donner, Blitzen, и, конечно, Rudolf."},
{"id": 50, "question": "❄️ Какой праздник отмечают 19 декабря в православии, когда детям дарят подарки?", "options": ["День святого Николая", "Рождественский сочельник", "Крещение", "Благовещение"], "correct": 0, "fact": "День святого Николая Чудотворца — это день, когда добрый святой (прообраз Деда Мороза) приносит детям подарки. На Западе его празднуют 6 декабря."},
{"id": 51, "question": "🎆 В какой стране на Новый год разбивают тарелки о двери друзей для привлечения удачи?", "options": ["🇩🇰 Дания", "🇬🇷 Греция", "🇮🇸 Исландия", "🇵🇱 Польша"], "correct": 0, "fact": "В Дании сохранилась странная, но весёлая традиция: чем больше черепков у порога твоего дома утром 1 января, тем больше у тебя друзей и, значит, удачи."},
{"id": 52, "question": "🕰️ Сколько ударов делают японские храмовые колокола в новогоднюю ночь?", "options": ["12", "100", "108", "1000"], "correct": 2, "fact": "108 ударов (дзёя-но канэ) символизируют очищение от 108 человеческих страстей и грехов, мешающих достичь просветления."},
{"id": 53, "question": "🍽️ Что является главным блюдом новогоднего стола во Вьетнаме?", "options": ["Суп «Фо»", "Баньтьынг (квадратные пироги)", "Рисовые лепёшки", "Спринг-роллы"], "correct": 1, "fact": "Баньтьынг — квадратные пироги из клейкого риса с мясной начинкой, завёрнутые в банановые листья. Их готовят в честь лунного Нового года (Тет)."},
{"id": 54, "question": "🎬 Как зовут мальчика, который остался «Один дома» на Рождество?", "options": ["Базз", "Гарри", "Кевин", "Билли"], "correct": 2, "fact": "Кевин МакКаллистер (в исполнении Макалея Калкина) — герой культовых рождественских фильмов «Один дома» (1990) и «Один дома 2» (1992)."},
{"id": 55, "question": "🧦 Из чего, по легенде, сделаны носки для подарков у Санты?", "options": ["Из овечьей шерсти", "Из красного бархата", "Из эльфийского трикотажа", "Не указано"], "correct": 3, "fact": "В классических историях и стихах материал носков не уточняется. Главное — они должны быть большими и висеть у камина!"},
{"id": 56, "question": "🎵 Какую песню поют в англоязычных странах, взявшись за руки в новогоднюю ночь?", "options": ["«We Wish You a Merry Christmas»", "«Jingle Bells»", "«Auld Lang Syne»", "«Happy New Year» ABBA"], "correct": 2, "fact": "«Auld Lang Syne» (старая шотландская песня, означающая «старые добрые времена») — неофициальный гимн проводов старого года."},
{"id": 57, "question": "🐟 Какое блюдо обязательно едят в ночь на 1 января в Польше для достатка?", "options": ["Сельдь", "Карп", "Осётр", "Лосось"], "correct": 1, "fact": "Чешуя карпа, которого готовят в Польше на Новый год, символизирует монетки и должна принести финансовую удачу."},
{"id": 58, "question": "🎭 Кто такие «Щедровки» или «Колядовщики»?", "options": ["Актеры рождественских спектаклей", "Люди, поющие колядки", "Мастера, делающие игрушки", "Повара, готовящие кутью"], "correct": 1, "fact": "Это группы людей (чаще молодёжь и дети), которые ходят от дома к дому с песнями-колядками, желая добра и получая угощения."},
{"id": 59, "question": "🌹 Что принято дарить на Рождество в Швеции, следуя традиции «Рождественского поросёнка»?", "options": ["Марципанового поросёнка", "Свиную ветчину", "Игрушку-хрюшку", "Копилку в форме свиньи"], "correct": 0, "fact": "Марципановые свинки — популярное рождественское лакомство и символ удачи в Швеции и других скандинавских странах."},
{"id": 60, "question": "🎄 Когда, по традиции, следует убирать новогоднюю ёлку?", "options": ["1 января", "7 января", "14 января", "19 января"], "correct": 2, "fact": "Суеверие гласит: если убрать ёлку до Старого Нового года (14 января), можно «отпугнуть» удачу. Хотя многие убирают после Рождества (7 января)."},
{"id": 61, "question": "🧙 Кто написал сказку «Щелкунчик и Мышиный король», лёгшую в основу балета?", "options": ["Братья Гримм", "Ганс Христиан Андерсен", "Эрнст Теодор Амадей Гофман", "Шарль Перро"], "correct": 2, "fact": "Сказку написал немецкий романтик Э.Т.А. Гофман в 1816 году. Позже Александр Дюма пересказал её в более мягком варианте, по которому и сделан балет."},
{"id": 62, "question": "🎅 Какой атрибут НЕ является частью традиционного образа Деда Мороза?", "options": ["Красная шуба", "Посох", "Очки", "Мешок с подарками"], "correct": 2, "fact": "Традиционный русский Дед Мороз не носит очки. Этот атрибут больше характерен для западного Санта-Клауса."},
{"id": 63, "question": "🇺🇸 Где в США проходит самая известная новогодняя церемония с падением шара?", "options": ["Лас-Вегас, Стрип", "Лос-Анджелес, Голливуд", "Нью-Йорк, Таймс-сквер", "Вашингтон, Белый дом"], "correct": 2, "fact": "Традиция падения светящегося шара на Таймс-сквер в Нью-Йорке существует с 1907 года и собирает миллионы зрителей."},
{"id": 64, "question": "🍰 Что такое «Королевский торт», который едят во Франции на Крещение (6 января)?", "options": ["Торт «Наполеон»", "Галетт де Руа", "Эклер", "Макарон"], "correct": 1, "fact": "Галетт де Руа — слоёный пирог с миндальным кремом, в который запекают маленькую фарфоровую фигурку (феве). Кто её найдёт, тот король на весь день!"},
{"id": 65, "question": "🎇 Что принято делать в первую секунду Нового года, по примете?", "options": ["Сесть на стул", "Позвонить родным", "Загадать желание", "Поцеловаться"], "correct": 2, "fact": "Самая популярная примета — успеть загадать самое сокровенное желание в первую минуту (или под бой курантов), и оно сбудется."},
{"id": 66, "question": "🎬 Какой фильм про волшебников стал новогодним хитом 1980-х в СССР?", "options": ["«Гостья из будущего»", "«Чародеи»", "«Мэри Поппинс, до свидания!»", "«Обыкновенное чудо»"], "correct": 1, "fact": "«Чародеи» (1982) с его знаменитым институтом магии, «правилом правой ноги» и песней «Три белых коня» — настоящая новогодняя классика."},
{"id": 67, "question": "🥂 Что значит французское выражение «Réveillon», популярное в праздники?", "options": ["Новогодний фейерверк", "Праздничный ужин", "Рождественская месса", "Новогодний бал"], "correct": 1, "fact": "«Рёвейон» — это обильный ночной праздничный ужин в канун Рождества (24 декабря) или Нового года (31 декабря)."},
{"id": 68, "question": "🎁 Что клали под ёлку в дореволюционной России, кроме подарков?", "options": ["Рождественский вертеп", "Свечи", "Подкову", "Венок из веток"], "correct": 0, "fact": "Рождественский вертеп — миниатюрная сцена с фигурками, изображающая пещеру, где родился Иисус. Это был важный символ праздника."},
{"id": 69, "question": "🕊️ Что символизирует рождественский венок из еловых веток?", "options": ["Колесо года", "Вечную жизнь", "Солнце и свет", "Все варианты верны"], "correct": 3, "fact": "Круглая форма — символ вечной жизни и солнца, зелёный цвет — жизни, свечи — свет, который осветит мир в день Рождества."},
{"id": 70, "question": "🎶 Как называется цикл зимних песен Вивальди из «Времён года»?", "options": ["«Весна»", "«Лето»", "«Осень»", "«Зима»"], "correct": 3, "fact": "«Зима» из цикла «Времена года» Антонио Вивальди — одно из самых узнаваемых классических произведений, ассоциирующихся с зимними праздниками."},
{"id": 71, "question": "🧧 Когда начинается и заканчивается празднование китайского Нового года?", "options": ["1 неделя", "2 недели", "15 дней", "1 месяц"], "correct": 2, "fact": "Празднование длится 15 дней, начиная с новолуния и заканчивая Праздником фонарей. Это самый длинный и важный праздник в Китае."},
{"id": 72, "question": "🎬 В каком фильме звучит фраза: «Есть ли жизнь на Марсе, нет ли жизни на Марсе — науке это неизвестно»?", "options": ["«Карнавальная ночь»", "«Бриллиантовая рука»", "«Операция «Ы»»", "«Иван Васильевич меняет профессию»"], "correct": 0, "fact": "Эту фразу произносит актёр Сергей Филиппов в роли лектора в фильме «Карнавальная ночь»."},
{"id": 73, "question": "🍬 Какой сладкий подарок в виде полена популярен на Рождество во Франции?", "options": ["Багет в шоколаде", "«Рождественское полено» (Бюш де Ноэль)", "Марципановое бревно", "Торт «Полено»"], "correct": 1, "fact": "«Бюш де Ноэль» — рулет, украшенный кремом и шоколадом, напоминающий настоящее полено, которое раньше сжигали в камине на Рождество для удачи."},
{"id": 74, "question": "🐕 Какой год по восточному календарю наступит после года Тигра?", "options": ["Кролика (Кота)", "Дракона", "Змеи", "Лошади"], "correct": 0, "fact": "12-летний цикл восточного календаря: Крыса, Бык, Тигр, Кролик (Кот), Дракон, Змея, Лошадь, Коза (Овца), Обезьяна, Петух, Собака, Свинья."},
{"id": 75, "question": "❄️ Какой город считается «родиной» Деда Мороза на Западе?", "options": ["Рованиеми (Финляндия)", "Нордпол (Аляска, США)", "Северный полюс (Канада)", "Тромсё (Норвегия)"], "correct": 0, "fact": "Рованиеми в финской Лапландии — официальная резиденция Йоулупукки (Санта-Клауса), куда приезжают тысячи туристов."},
{"id": 76, "question": "🕰️ Как называется старый стиль летоисчисления, по которому отмечают Старый Новый год?", "options": ["Григорианский календарь", "Юлианский календарь", "Лунный календарь", "Коптский календарь"], "correct": 1, "fact": "Разница между старым (Юлианским) и новым (Григорианским) стилем в XX-XXI веках составляет 13 дней, отсюда и дата 14 января."},
{"id": 77, "question": "🎄 Что клали на макушку рождественской ёлки до появления Вифлеемской звезды?", "options": ["Шестиконечную звезду", "Свечу", "Куколку", "Яблоко"], "correct": 1, "fact": "До распространения пятиконечной звезды как символа Вифлеемской, верхушку венчала зажжённая свеча, что, конечно, было пожароопасно."},
{"id": 78, "question": "🍽️ Что такое «сочиво» или «кутья», которую едят в рождественский сочельник?", "options": ["Каша с мёдом и орехами", "Постные блины", "Тушёные овощи", "Грибной суп"], "correct": 0, "fact": "Это ритуальное постное блюдо из варёной пшеницы (риса, чечевицы) с мёдом, орехами и маком. Символизирует плодородие и благополучие."},
{"id": 79, "question": "🎅 Как переводится с английского имя «Santa Claus»?", "options": ["Святой Николай", "Зимний волшебник", "Рождественский дед", "Добрый даритель"], "correct": 0, "fact": "Имя произошло от голландского «Sinterklaas» (Святой Николас), которое эмигранты привезли в Америку, где оно трансформировалось в Santa Claus."},
{"id": 80, "question": "🎬 Какой новогодний мультфильм про снежного человека стал классикой?", "options": ["«Снеговик-почтовик»", "«Дед Мороз и Серый волк»", "«Умка»", "«Зима в Простоквашино»"], "correct": 0, "fact": "«Снеговик-почтовик» (1955) по сказке Сутеева — трогательная история о снеговике, который отправляется к Деду Морозу за ёлкой для детей."},
{"id": 81, "question": "🥂 Что пьют в Германии на Новый год под названием «Feuerzangenbowle»?", "options": ["Горячее пиво с ромом", "Глинтвейн", "Шампанское с ликёром", "Пунш"], "correct": 0, "fact": "«Фойерцангенболе» — это традиционный немецкий алкогольный напиток на основе глинтвейна, в который добавляют сахарную голову, пропитанную ромом, и поджигают!"},
{"id": 82, "question": "🎁 В какой стране подарки детям 6 декабря приносит Святой Николай, а 25 декабря — Кристкинд («Младенец Христос»)?", "options": ["🇦🇹 Австрия", "🇮🇹 Италия", "🇪🇸 Испания", "🇷🇺 Россия"], "correct": 0, "fact": "В Австрии и части Германии существует разделение: скромные подарки от Николая и основные — от Кристкинда, ангелоподобного существа."},
{"id": 83, "question": "🎆 Что делают жители Эквадора на Новый год, сжигая чучела?", "options": ["Сжигают список плохих поступков", "Сжигают фотографии бывших", "Сжигают старые вещи", "Все варианты верны"], "correct": 3, "fact": "Эквадорцы мастерят чучела («años viejos») из старых вещей, вкладывают в них списки неприятностей и в полночь сжигают, очищаясь для нового года."},
{"id": 84, "question": "🐖 Что нельзя делать в первые дни Нового года по китайским поверьям?", "options": ["Подметать пол", "Стричься", "Плакать и ругаться", "Все варианты верны"], "correct": 3, "fact": "Всё это, по поверьям, может «вымести» или «отрезать» удачу, привлечь слёзы и ссоры на весь грядущий год."},
{"id": 85, "question": "🎶 Кто исполнил знаменитую новогоднюю песню «Happy New Year»?", "options": ["The Beatles", "ABBA", "Queen", "Modern Talking"], "correct": 1, "fact": "Эта немного грустная, но красивая песня — творчество шведской группы ABBA, выпущенное в 1980 году."},
{"id": 86, "question": "🧹 С чем, по славянскому поверью, связан приход Деда Мороза в дом?", "options": ["С морозом на окнах", "С инеем на бороде", "Со скрипом половиц", "Со снежной метелью"], "correct": 0, "fact": "Считалось, что Дед Мороз, проходя мимо, «морозит» стёкла окон своими волшебными узорами."},
{"id": 87, "question": "🎄 Какой цвет был у первых искусственных ёлочных игрушек?", "options": ["Серебряный", "Красный", "Синий", "Золотой"], "correct": 0, "fact": "Первые украшения в Германии были очень простыми: яблоки (красные), вафли (золотистые), но первые искусственные игрушки из тонкого листового олова имитировали серебро."},
{"id": 88, "question": "🎬 Какой фильм НЕ считается новогодним в России, хотя его действие происходит зимой?", "options": ["«Джентльмены удачи»", "«С лёгким паром!»", "«Морозко»", "«Сибирский цирюльник»"], "correct": 3, "fact": "«Сибирский цирюльник» — историческая драма, а не новогодняя комедия. А вот «Джентльмены удачи» с их «гранатой в кармане» стали любимыми благодаря новогодним показам."},
{"id": 89, "question": "🧧 Что дарят на Новый год в Шотландии, чтобы принести в дом удачу?", "options": ["Кусочек угля", "Пирог с сюрпризом", "Веточку омелы", "Серебряную монету"], "correct": 0, "fact": "Старинный шотландский обычай «first-footing»: первый готь в новом году должен быть темноволосым мужчиной и принести с собой уголь, виски, хлеб и монету — символы тепла, веселья, пищи и богатства."},
{"id": 90, "question": "🎅 Кто, согласно стихотворению, «не подарят нам, а сам всё возьмёт»?", "options": ["Снегурочка", "Снеговик", "Снежная Королева", "Морозко"], "correct": 3, "fact": "Это строка из детского стихотворения Самуила Маршака «Морозко»: «Не грозит нам здесь беда, / Не возьмёт нас Морозко — / Не подарят нам, а сам / Всё возьмёт!»"},
{"id": 91, "question": "🥟 Сколько пельменей нужно съесть на Новый год, чтобы весь год был сытым (по шуточной примете)?", "options": ["7 (по дням недели)", "12 (по месяцам)", "31 (по дням месяца)", "100 (на всякий случай)"], "correct": 1, "fact": "Шуточная, но популярная примета: съесть 12 пельменей (по одному на каждый месяц) — и год будет сытым и удачным."},
{"id": 92, "question": "🎇 В какой стране на Новый год бьют посуду для изгнания злых духов?", "options": ["🇨🇳 Китай", "🇩🇪 Германия", "🇮🇹 Италия", "Все варианты верны"], "correct": 3, "fact": "Похожие традиции есть у многих народов. Например, в Дании бьют тарелки о двери друзей, а в Германии и Китае шум и грохот должны отпугнуть зло."},
{"id": 93, "question": "🎁 Что дарят в Голландии на день Святого Николая (5 декабря), кладя в башмаки?", "options": ["Монеты шоколадные", "Имбирные пряники", "Подарочные сертификаты", "Мелкие игрушки и сладости"], "correct": 3, "fact": "Дети ставят башмаки у камина или двери, а утром находят в них маленькие подарки, сладости (часто — первые буквы их имён из шоколада) и мандарины."},
{"id": 94, "question": "🎬 В каком фильме прозвучала фраза: «Надо, Федя, надо…» в новогоднюю ночь?", "options": ["«Карнавальная ночь»", "«Ирония судьбы»", "«Голубой огонёк»", "«Служебный роман»"], "correct": 1, "fact": "Эту фразу говорит Ипполит (Юрий Яковлев) своему другу Феде в фильме «Ирония судьбы, или С лёгким паром!»."},
{"id": 95, "question": "🧙 Какое растение считается символом Рождества и под ним принято целоваться?", "options": ["Омела", "Падуб (остролист)", "Плющ", "Ель"], "correct": 0, "fact": "Традиция поцелуев под омелой пришла из английского фольклора. Считалось, что она приносит счастье и защищает от зла."},
{"id": 96, "question": "🍊 Почему мандарины стали традиционным новогодним фруктом в СССР?", "options": ["Их привозили из Абхазии как раз к зиме", "Это символ солнца в разгар зимы", "Они были дешёвыми", "Все варианты верны"], "correct": 3, "fact": "Всё вместе: мандарины из Абхазии созревали как раз к Новому году, были доступны по цене, а их яркий цвет и запах ассоциировались с праздником и солнцем."},
{"id": 97, "question": "🎄 Как называется день, когда ёлку вносят в дом и наряжают?", "options": ["День украшения ёлки", "Ёлочный день", "Сочельник", "У него нет специального названия"], "correct": 3, "fact": "Хотя в каждой семье есть своя традиция (чаще после 20 декабря), единого календарного дня для украшения ёлки не существует."},
{"id": 98, "question": "🦌 Сколько всего оленей в упряжке Санта-Клауса (без Рудольфа)?", "options": ["6", "7", "8", "9"], "correct": 2, "fact": "Классическая упряжка состоит из восьми оленей: Dasher, Dancer, Prancer, Vixen, Comet, Cupid, Donner, Blitzen. Рудольф присоединился позже как девятый и ведущий."},
{"id": 99, "question": "🥂 Что кричат в новогоднюю ночь в России, когда чокаются бокалами?", "options": ["«Ура!»", "«С Новым годом!»", "«За встречу!»", "Любое из вышеперечисленного"], "correct": 3, "fact": "Нет строгого правила! Чаще всего звучит простое и радостное «С Новым годом!» или «Ура!», но можно придумать и свой тост."},
{"id": 100, "question": "❄️ Как заканчивается знаменитая новогодняя фраза из фильма: «С Новым годом, с новым…»?", "options": ["…счастьем!»", "…везением!»", "…богатством!»", "…настроением!»"], "correct": 0, "fact": "Фраза из фильма «Карнавальная ночь» в исполнении Юрия Никулина: «С Новым годом, с новым счастьем!» стала крылатой и самой популярной для поздравлений."},
]

async def game_quiz_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    quiz_info = """
🎓 <b>Новогодний квиз</b>

Проверь свои знания о Новом годе и Рождестве!

<b>Правила:</b>
• 5 случайных вопросов
• За каждый правильный ответ - 10 очков
• Идеальный результат - 50 очков
• Узнавай интересные факты

<b>💡 Совет:</b> Внимательно читай вопросы и варианты ответов

Готов начать?
"""
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 Начать квиз", callback_data="quiz_start")],
        [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
    ])
    
    await q.edit_message_text(quiz_info, parse_mode='HTML', reply_markup=kb)

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    user = update.effective_user
    init_user_data(user.id)
    
    # Получаем вопросы, на которые пользователь еще не отвечал
    answered_ids = set(user_data[str(user.id)].get("answered_quiz_questions", []))
    available_questions = [q for q in NEW_YEAR_QUIZ if q["id"] not in answered_ids]
    
    # Проверяем, есть ли доступные вопросы
    if not available_questions:
        await update.callback_query.edit_message_text(
            "🎓 <b>Поздравляем! 🎉</b>\n\n"
            "Ты ответил на все вопросы новогоднего квиза!\n\n"
            "Новые вопросы появятся в следующем обновлении бота. 🎄",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Топ игроков", callback_data="quiz_top")],
                [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
            ])
        )
        return
    
    # Выбираем 5 случайных вопросов из доступных
    questions = random.sample(available_questions, min(5, len(available_questions)))
    
    context.user_data["quiz"] = {
        "score": 0,
        "current_question": 0,
        "questions": questions,
        "answers": []
    }
    
    await ask_quiz_question(update, context)

async def ask_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz_data = context.user_data.get("quiz")
    
    if not quiz_data:
        # Если данных нет, начинаем заново
        await update.callback_query.answer("❌ Данные квиза потеряны. Начинаем заново!", show_alert=True)
        await start_quiz(update, context)
        return
    
    current_q = quiz_data["current_question"]
    
    # Проверяем, не закончились ли вопросы
    if current_q >= len(quiz_data["questions"]):
        await finish_quiz(update, context)
        return
    
    question_data = quiz_data["questions"][current_q]
    
    keyboard = []
    for i, option in enumerate(question_data["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"quiz_answer_{i}")])
    
    progress = f"({current_q + 1}/{len(quiz_data['questions'])})"
    
    await update.callback_query.edit_message_text(
        f"🎓 <b>НОВОГОДНИЙ КВИЗ {progress}</b>\n\n"
        f"❓ {question_data['question']}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    user_answer = int(q.data.split("_")[2])
    quiz_data = context.user_data["quiz"]
    current_q = quiz_data["current_question"]
    question_data = quiz_data["questions"][current_q]
    
    is_correct = user_answer == question_data["correct"]
    quiz_data["answers"].append({
        "question": question_data["question"],
        "user_answer": user_answer,
        "correct_answer": question_data["correct"],
        "is_correct": is_correct,
        "question_id": question_data["id"]
    })
    
    if is_correct:
        quiz_data["score"] += 10
        result_text = "✅ <b>Правильно!</b> +10 очков"
    else:
        correct_answer = question_data["options"][question_data["correct"]]
        result_text = f"❌ <b>Неправильно!</b> Правильный ответ: {correct_answer}"
    
    result_text += f"\n\n💡 {question_data['fact']}"
    
    # Проверяем, был ли это последний вопрос
    if current_q + 1 >= len(quiz_data["questions"]):
        # Это последний вопрос - сразу завершаем
        keyboard = [[InlineKeyboardButton("📊 Посмотреть результаты", callback_data="quiz_finish_now")]]
    else:
        # Ещё есть вопросы
        keyboard = [[InlineKeyboardButton("➡️ Следующий вопрос", callback_data="quiz_next")]]
    
    await q.edit_message_text(
        result_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def quiz_next_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    quiz_data = context.user_data.get("quiz")
    if not quiz_data:
        await update.callback_query.edit_message_text(
            "❌ Данные квиза потеряны. Начинаем заново!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 Начать квиз", callback_data="quiz_start")]
            ])
        )
        return
    
    quiz_data["current_question"] += 1
    await ask_quiz_question(update, context)

async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение квиза и вывод результатов"""
    quiz_data = context.user_data["quiz"]
    score = quiz_data["score"]
    total = len(quiz_data["questions"]) * 10
    
    user = update.effective_user
    init_user_data(user.id)
    
    correct_answers = sum(1 for answer in quiz_data["answers"] if answer["is_correct"])
    total_questions = len(quiz_data["questions"])
    
    # 🔥 ПРОВЕРКА ДОСТИЖЕНИЯ 333 БАЛЛОВ
    old_quiz_points = user_data[str(user.id)].get("quiz_points", 0)
    new_quiz_points = old_quiz_points + score
    
    # Обновляем статистику в глобальной переменной
    user_data[str(user.id)]["quiz_points"] = new_quiz_points
    user_data[str(user.id)]["total_quiz_correct"] = user_data[str(user.id)].get("total_quiz_correct", 0) + correct_answers
    user_data[str(user.id)]["total_quiz_played"] = user_data[str(user.id)].get("total_quiz_played", 0) + 1
    
    # Проверяем, достиг ли пользователь 333 баллов
    congratulated_333 = user_data[str(user.id)].get("congratulated_333", False)
    just_reached_333 = False
    
    if not congratulated_333 and new_quiz_points >= 333 and old_quiz_points < 333:
        just_reached_333 = True
        user_data[str(user.id)]["congratulated_333"] = True
        
    if correct_answers == total_questions:
        user_data[str(user.id)]["quiz_wins"] = user_data[str(user.id)].get("quiz_wins", 0) + 1
        result_message = "🎉 <b>ИДЕАЛЬНО! Ты настоящий новогодний эксперт!</b>"
    elif correct_answers >= total_questions * 0.7:
        result_message = "🎊 <b>Отличный результат! Ты хорошо знаешь новогодние традиции!</b>"
    elif correct_answers >= total_questions * 0.5:
        result_message = "👍 <b>Хороший результат! Есть что вспомнить о Новом годе!</b>"
    else:
        result_message = "📚 <b>Неплохо! Новогодние традиции — это интересно!</b>"
    
    # Сохраняем отвеченные вопросы
    for answer in quiz_data["answers"]:
        question_id = answer.get("question_id")
        if question_id and question_id not in user_data[str(user.id)]["answered_quiz_questions"]:
            user_data[str(user.id)]["answered_quiz_questions"].append(question_id)
    
    # 🔥 ВАЖНО: Сохраняем данные правильно
    # Загружаем текущие данные из файла
    file_data = load_all_data()
    
    # Обновляем только данные текущего пользователя
    file_data["users"][str(user.id)] = user_data[str(user.id)]
    
    # Сохраняем обратно в файл
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Данные квиза сохранены для пользователя {user.id}")
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")
    
    data = load_all_data()
    save_all_data(data)
    print(f"✅ Данные квиза сохранены для пользователя {user.id}")

    # 🔥 ПОДГОТОВКА ПОЗДРАВЛЕНИЯ С 333 БАЛЛАМИ
    congrats_text = ""
    if just_reached_333:
        congrats_text = f"""
🎺 <b>🎶 МУЗЫКАЛЬНАЯ НАГРАДА! 🎶</b>

🏆 <b>ТЫ ДОСТИГ 333 БАЛЛОВ В КВИЗЕ!</b>
💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥💥
Это особое достижение! Ты настоящий эксперт по новогодним традициям!
Тебе открывается секретная музыкальная награда...
"""
    
    # Формируем итоговое сообщение
    final_text = f"""
🎓 <b>НОВОГОДНИЙ КВИЗ ЗАВЕРШЁН!</b>

{result_message}

📊 <b>ТВОЙ РЕЗУЛЬТАТ:</b>
• Правильных ответов: {correct_answers}/{total_questions}
• Получено очков: {score}/{total}
• Всего очков за все игры: {user_data[str(user.id)]['quiz_points']}

🎄 <b>Статистика:</b>
• Сыграно квизов: {user_data[str(user.id)]['total_quiz_played']}
• Правильных ответов за всё время: {user_data[str(user.id)]['total_quiz_correct']}
• Побед (идеальных результатов): {user_data[str(user.id)].get('quiz_wins', 0)}

{congrats_text if congrats_text else ''}
Хочешь попробовать ещё раз?
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="game_quiz")],
        [InlineKeyboardButton("📊 Топ игроков", callback_data="quiz_top")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
    ]
    
    # Проверяем, есть ли callback_query
    if update.callback_query:
        await update.callback_query.edit_message_text(
            final_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # На всякий случай, если нет callback_query
        await update.message.reply_text(
            final_text,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # 🔥 ОТПРАВКА МУЗЫКАЛЬНОГО ФАЙЛА ПРИ 333 БАЛЛАХ
    if just_reached_333:
        await send_333_congrats_audio(update, context, user.id)
    
    # Очищаем данные квиза из контекста
    if "quiz" in context.user_data:
        del context.user_data["quiz"]

async def send_333_congrats_audio(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Отправка музыкального файла при достижении 333 баллов"""
    try:
        # Способ 1: Отправка по URL
        if CONGRATS_AUDIO_URL.startswith("https"):
            # Если это URL
            await context.bot.send_audio(
                chat_id=user_id,
                audio=CONGRATS_AUDIO_URL,
                caption="🎶 Твоя награда за 333 балла в квизе! Поздравляем! 🏆",
                title="Музыкальная награда за 333 балла",
                performer="Secret Santa Bot",
                parse_mode='HTML'
            )
        
        # Способ 2: Отправка локального файла (для Replit)
        else:
            try:
                with open(CONGRATS_AUDIO_URL, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=user_id,
                        audio=audio_file,
                        caption="🎶 Твоя награда за 333 балла в квизе! Поздравляем! 🏆",
                        title="Музыкальная награда за 333 балла",
                        performer="Secret Santa Bot",
                        parse_mode='HTML'
                    )
            except FileNotFoundError:
                # Если файл не найден, отправляем поздравление без музыки
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 <b>Особое достижение!</b>\n\n"
                         "Ты достиг 333 баллов в квизе!\n"
                         "К сожалению, музыкальная награда временно недоступна, "
                         "но твоё достижение записано! 🏆",
                    parse_mode='HTML'
                )
        
        print(f"✅ Музыкальная награда отправлена пользователю {user_id}")
        
    except Exception as e:
        print(f"❌ Ошибка отправки музыкальной награды: {e}")
        # В случае ошибки отправляем текстовое поздравление
        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 <b>Особое достижение!</b>\n\n"
                 "Ты достиг 333 баллов в квизе!\n"
                 "Это невероятный результат! Ты настоящий новогодний эксперт! 🏆",
            parse_mode='HTML'
        )

async def show_quiz_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    
    # Загружаем актуальные данные
    data = load_all_data()
    users = data.get("users", {})
    
    if not users:
        await update.callback_query.edit_message_text(
            "🏆 <b>ТОП ИГРОКОВ КВИЗА</b>\n\n"
            "Пока никто не играл в квиз. Будь первым! 🎄",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 Играть в квиз", callback_data="game_quiz")],
                [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
            ])
        )
        return
    
    # Собираем статистику всех игроков, которые играли в квиз
    player_stats = []
    
    for user_id_str, user_info in users.items():
        # Проверяем, играл ли пользователь в квиз
        total_played = user_info.get("total_quiz_played", 0)
        quiz_points = user_info.get("quiz_points", 0)
        
        # Включаем в топ только тех, кто набрал хоть какие-то очки
        if total_played > 0 or quiz_points > 0:
            quiz_wins = user_info.get("quiz_wins", 0)
            total_correct = user_info.get("total_quiz_correct", 0)
            total_played = user_info.get("total_quiz_played", 0)
            
            # Вычисляем точность
            accuracy = 0
            if total_played > 0:
                accuracy = (total_correct / (total_played * 5)) * 100
            
            player_stats.append({
                "id": user_id_str,
                "name": user_info.get("name", "Неизвестный"),
                "username": user_info.get("username", ""),
                "points": quiz_points,
                "wins": quiz_wins,
                "accuracy": accuracy,
                "played": total_played,
                "correct": total_correct
            })
    
    # Сортируем по очкам (по убыванию), затем по победам
    player_stats.sort(key=lambda x: (x["points"], x["wins"]), reverse=True)
    
    top_text = "🏆 <b>ТОП ИГРОКОВ КВИЗА</b>\n\n"
    
    if not player_stats:
        top_text += "Пока никто не играл в квиз. Будь первым! 🎄\n\n"
    else:
        medals = ["🥇", "🥈", "🥉"]
        for i, player in enumerate(player_stats[:20]):  # Показываем до 20 игроков
            if i < 3:
                medal = medals[i]
            else:
                medal = f"{i+1}."
            
            display_name = player["name"][:20] + "..." if len(player["name"]) > 20 else player["name"]
            username_display = f"(@{player['username']})" if player["username"] and player["username"] != "без username" else ""
            
            top_text += f"{medal} <b>{display_name}</b> {username_display}\n"
            top_text += f"   📊 Очки: {player['points']} | 🏆 Побед: {player['wins']} | 🎯 Точность: {player['accuracy']:.1f}%\n\n"
    
    # Общая статистика
    top_text += "🎮 <b>ОБЩАЯ СТАТИСТИКА:</b>\n"
    top_text += f"• Всего игроков в квизе: {len(player_stats)}\n"
    top_text += f"• Всего сыграно квизов: {sum(p['played'] for p in player_stats)}\n"
    top_text += f"• Всего правильных ответов: {sum(p['correct'] for p in player_stats)}\n"
    
    if player_stats:
        avg_accuracy = sum(p['accuracy'] for p in player_stats) / len(player_stats)
        top_text += f"• Средняя точность: {avg_accuracy:.1f}%"
    else:
        top_text += "• Средняя точность: 0%"
    
    await update.callback_query.edit_message_text(
        top_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Играть в квиз", callback_data="game_quiz")],
            [InlineKeyboardButton("⬅️ Назад в игры", callback_data="mini_games")]
        ])
    )
# -------------------------------------------------------------------
# 📊 РАЗДЕЛ: ПРОФИЛЬ И СТАТИСТИКА
# -------------------------------------------------------------------
async def enhanced_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_all_data()
    users = data.get("users", {})
    user_info = users.get(str(user.id), {})
    user = update.effective_user
    init_user_data(user.id)
    
    user_info = user_data[str(user.id)]
    
    # Статистика квиза
    quiz_points = user_info.get("quiz_points", 0)
    quiz_wins = user_info.get("quiz_wins", 0)
    total_correct = user_info.get("total_quiz_correct", 0)
    total_played = user_info.get("total_quiz_played", 0)
    accuracy = (total_correct / (total_played * 5)) * 100 if total_played > 0 else 0
    
    # Проверка достижения 333 баллов
    has_333_achievement = quiz_points >= 333
    congratulated_333 = user_info.get("congratulated_333", False)
    
    # Статистика битв с Гринчем
    grinch_fights = user_info.get("grinch_fights", 0)
    grinch_wins = user_info.get("grinch_wins", 0)
    win_rate = (grinch_wins / grinch_fights * 100) if grinch_fights > 0 else 0
    
    profile_text = f"""
🎅 <b>Профиль игрока</b> @{user.username if user.username else user.first_name}

🎓 <b>Статистика квиза:</b>
• Очки: {quiz_points}
• Побед: {quiz_wins}
• Сыграно игр: {total_played}
• Правильных ответов: {total_correct}
• Точность: {accuracy:.1f}%
{'' if not has_333_achievement else '• 🏆 Достижение 333 баллов: ✅ Получено!'}
{'' if has_333_achievement and not congratulated_333 else ''}

⚔️ <b>Битвы с Гринчем:</b>
• Всего битв: {grinch_fights}
• Побед: {grinch_wins}
• Процент побед: {win_rate:.1f}%

🎖 <b>Достижения:</b> {len(user_info.get('achievements', []))}
"""
    
    # Находим комнату пользователя
    data = load_all_data()
    for code, room in data["rooms"].items():
        if str(user.id) in room["members"]:
            profile_text += f"\n🏠 <b>Текущая комната:</b> {code}"
            break
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            profile_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            profile_text, 
            parse_mode='HTML',
            reply_markup=back_to_menu_keyboard()
        )
# -------------------------------------------------------------------
# ⚙️ РАЗДЕЛ: АДМИН-ПАНЕЛЬ
# -------------------------------------------------------------------
async def start_game_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён.", show_alert=True)
        return

    data = load_all_data()
    
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
    data = load_all_data()
    
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
    save_all_data(data)

    successful_sends = 0
    for giver, receiver in assigns.items():
        m = room["members"][str(receiver)]
        try:
            await context.bot.send_message(
                giver,
                f"🎁 <b>Тайный Санта запущен!</b> 🎄\n\n"
                f"<b>Твой получатель:</b> {m['name']} (@{m['username']})\n\n"
                f"✨ <b>Его пожелание:</b> {m['wish']}\n\n"
                f"<b>💡 Что делать:</b>\n"
                f"1. Купи или сделай подарок\n"
                f"2. Передай его получателю\n"
                f"3. Не раскрывай себя до вручения!\n\n"
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
        f"Все участники получили своих получателей! 🎁\n\n"
        f"<b>💡 Информация для игроков:</b>\n"
        f"• Они видят только своего получателя\n"
        f"• Не видят, кто дарит им подарок\n"
        f"• Игра продолжается до вручения всех подарков",
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def delete_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    data = load_all_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard = []
    for code, room in data["rooms"].items():
        status = "✅ Активна" if room["game_started"] else "⏳ Ожидание"
        keyboard.append([InlineKeyboardButton(f"🗑️ {code} ({len(room['members'])} участ.) - {status}", callback_data=f"delete_{code}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "🗑️ <b>Удаление комнат</b>\n\n"
        "Выбери комнату для удаления:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def delete_specific_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    code = q.data.replace("delete_", "")
    data = load_all_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return
    
    room = data["rooms"][code]
    
    # Уведомляем участников об удалении комнаты
    for member_id in room["members"]:
        try:
            await context.bot.send_message(
                member_id,
                f"❌ <b>Комната {code} была удалена администратором.</b>\n\n"
                f"Если ты ещё не получил подарок, свяжись с организатором игры.",
                parse_mode='HTML'
            )
        except:
            pass
    
    del data["rooms"][code]
    save_all_data(data)
    
    await q.edit_message_text(
        f"✅ <b>Комната {code} успешно удалена!</b>\n\n"
        f"<b>Участников было:</b> {len(room['members'])}\n"
        f"<b>Статус игры:</b> {'Активна' if room['game_started'] else 'Не запущена'}",
        parse_mode='HTML',
        reply_markup=back_to_menu_keyboard(True)
    )

async def admin_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    data = load_all_data()
    total_users = len(user_data)
    
    total_games_won = sum(data.get("games_won", 0) for data in user_data.values())
    total_grinch_wins = sum(data.get("grinch_wins", 0) for data in user_data.values())
    total_quiz_points = sum(data.get("quiz_points", 0) for data in user_data.values())
    
    stats_text = f"""
📊 <b>АДМИН СТАТИСТИКА</b>

👥 <b>Пользователи:</b>
• Всего пользователей: {total_users}

🎮 <b>Общая игровая статистика:</b>
• Всего побед в играх: {total_games_won}
• Побед над Гринчем: {total_grinch_wins}
• Всего очков в квизе: {total_quiz_points}

🏠 <b>Статистика комнат:</b>
"""
    
    total_rooms = len(data["rooms"])
    active_rooms = sum(1 for room in data["rooms"].values() if room["game_started"])
    total_participants = sum(len(room["members"]) for room in data["rooms"].values())
    
    stats_text += f"""
• Всего комнат: {total_rooms}
• Активных игр: {active_rooms}
• Всего участников: {total_participants}
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
# 📋 АДМИН: ПРОСМОТР РАСПРЕДЕЛЕНИЯ И ПОЖЕЛАНИЙ
# -------------------------------------------------------------------
async def admin_view_distribution_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню просмотра распределения и пожеланий"""
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    data = load_all_data()
    
    if not data["rooms"]:
        await update.callback_query.edit_message_text(
            "🚫 Нет созданных комнат!",
            reply_markup=back_to_menu_keyboard(True)
        )
        return
    
    keyboard = []
    for code, room in data["rooms"].items():
        status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
        members_count = len(room["members"])
        keyboard.append([InlineKeyboardButton(
            f"📊 {code} ({members_count} участ.) - {status}", 
            callback_data=f"view_dist_{code}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")])
    
    await update.callback_query.edit_message_text(
        "📋 <b>Просмотр распределения и пожеланий</b>\n\n"
        "Выбери комнату для просмотра:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_view_distribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать распределение и пожелания в комнате"""
    q = update.callback_query
    await q.answer()
    
    if not is_admin(update):
        await q.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    code = q.data.replace("view_dist_", "")
    data = load_all_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return
    
    room = data["rooms"][code]
    
    # Формируем текст с пожеланиями
    wishes_text = "<b>🎁 ПОЖЕЛАНИЯ ВСЕХ УЧАСТНИКОВ:</b>\n\n"
    for i, (user_id, member) in enumerate(room["members"].items(), 1):
        wish = member["wish"] if member["wish"] else "❌ Не указано"
        username = f"@{member['username']}" if member["username"] and member["username"] != "без username" else "без username"
        wishes_text += f"<b>{i}. {member['name']} ({username}):</b>\n{wish}\n\n"
    
    # Формируем текст с распределением (если игра запущена)
    distribution_text = ""
    if room["game_started"] and room["assign"]:
        distribution_text = "<b>🎯 РАСПРЕДЕЛЕНИЕ ПОДАРКОВ:</b>\n\n"
        for giver_id, receiver_id in room["assign"].items():
            giver = room["members"][giver_id]["name"]
            receiver = room["members"][receiver_id]["name"]
            giver_username = room["members"][giver_id]["username"]
            receiver_username = room["members"][receiver_id]["username"]
            
            giver_display = f"@{giver_username}" if giver_username and giver_username != "без username" else "без username"
            receiver_display = f"@{receiver_username}" if receiver_username and receiver_username != "без username" else "без username"
            
            distribution_text += f"🎅 <b>{giver}</b> ({giver_display})\n   ↓ дарит подарок ↓\n🎁 <b>{receiver}</b> ({receiver_display})\n\n"
    
    full_text = f"""
<b>📋 КОМНАТА: {code}</b>

<b>Статус:</b> {'✅ Игра запущена' if room['game_started'] else '⏳ Ожидание запуска'}
<b>Участников:</b> {len(room['members'])}
<b>Создатель:</b> {room['creator']}
<b>Создана:</b> {datetime.fromisoformat(room['created_at']).strftime('%d.%m.%Y %H:%M')}

{'-'*40}

{wishes_text}

{distribution_text if distribution_text else ''}
"""
    
    keyboard = [
        [InlineKeyboardButton("📤 Экспорт в файл", callback_data=f"export_room_{code}")],
        [InlineKeyboardButton("🔄 Сбросить игру", callback_data=f"reset_game_{code}")],
        [InlineKeyboardButton("🗑️ Удалить комнату", callback_data=f"delete_{code}")],
        [InlineKeyboardButton("⬅️ Назад к списку", callback_data="admin_view_distribution_menu")]
    ]
    
    await q.edit_message_text(
        full_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбросить игру в комнате (очистить распределение)"""
    q = update.callback_query
    await q.answer()
    
    if not is_admin(update):
        await q.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    code = q.data.replace("reset_game_", "")
    data = load_all_data()
    
    if code not in data["rooms"]:
        await q.edit_message_text("🚫 Комната не найдена!")
        return
    
    room = data["rooms"][code]
    
    if not room["game_started"]:
        await q.answer("❌ Игра ещё не запущена!", show_alert=True)
        return
    
    # Сбрасываем игру
    room["game_started"] = False
    room["assign"] = {}
    save_all_data(data)
    
    # Уведомляем участников
    for member_id in room["members"]:
        try:
            await context.bot.send_message(
                member_id,
                f"🔄 <b>Игра в комнате {code} сброшена администратором!</b>\n\n"
                f"Распределение подарков было отменено. "
                f"Ожидайте нового запуска игры от организатора.",
                parse_mode='HTML'
            )
        except:
            pass
    
    await q.edit_message_text(
        f"🔄 <b>Игра в комнате {code} успешно сброшена!</b>\n\n"
        f"<b>Участников:</b> {len(room['members'])}\n"
        f"<b>Статус:</b> Ожидание запуска\n\n"
        f"Все участники получили уведомление.",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Просмотр комнаты", callback_data=f"view_dist_{code}")],
            [InlineKeyboardButton("🚀 Запустить игру", callback_data=f"start_{code}")],
            [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
        ])
    )

async def admin_export_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экспорт данных комнаты в текстовый файл"""
    q = update.callback_query
    await q.answer()
    
    if not is_admin(update):
        await q.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    code = q.data.replace("export_room_", "")
    data = load_all_data()
    
    if code not in data["rooms"]:
        await q.answer("❌ Комната не найдена!", show_alert=True)
        return
    
    room = data["rooms"][code]
    
    # Формируем содержимое файла
    file_content = f"ДАННЫЕ КОМНАТЫ ТАЙНОГО САНТЫ\n"
    file_content += f"Код комнаты: {code}\n"
    file_content += f"Статус: {'Игра запущена' if room['game_started'] else 'Ожидание'}\n"
    file_content += f"Участников: {len(room['members'])}\n"
    file_content += f"Создана: {datetime.fromisoformat(room['created_at']).strftime('%d.%m.%Y %H:%M')}\n"
    file_content += f"\n{'='*50}\n\n"
    
    # Участники и пожелания
    file_content += "УЧАСТНИКИ И ПОЖЕЛАНИЯ:\n"
    for i, (user_id, member) in enumerate(room["members"].items(), 1):
        wish = member["wish"] if member["wish"] else "Не указано"
        file_content += f"\n{i}. {member['name']} (@{member['username']})\n"
        file_content += f"   ID: {user_id}\n"
        file_content += f"   Пожелание: {wish}\n"
    
    # Распределение (если есть)
    if room["game_started"] and room["assign"]:
        file_content += f"\n{'='*50}\n\n"
        file_content += "РАСПРЕДЕЛЕНИЕ ПОДАРКОВ:\n\n"
        for giver_id, receiver_id in room["assign"].items():
            giver = room["members"][giver_id]["name"]
            receiver = room["members"][receiver_id]["name"]
            file_content += f"🎅 {giver} → 🎁 {receiver}\n"
    
    # Сохраняем во временный файл
    filename = f"room_{code}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(file_content)
    
    # Отправляем файл
    with open(filename, "rb") as f:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=f,
            filename=filename,
            caption=f"📁 Экспорт данных комнаты {code}\n"
                   f"👥 Участников: {len(room['members'])}\n"
                   f"🎮 Статус: {'Игра активна' if room['game_started'] else 'Ожидание'}"
        )
    
    # Удаляем временный файл
    import os
    os.remove(filename)
    
    await q.answer("✅ Файл отправлен!", show_alert=True)

async def admin_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск пользователя по имени или username"""
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    search_instructions = """
🔍 <b>Поиск пользователя</b>

Введи имя пользователя или его username для поиска:

💡 <b>Примеры запросов:</b>
• "Иван" - поиск по имени
• "@username" - поиск по username
• "Иван Петров" - поиск по полному имени

Поиск осуществляется по всем пользователям бота.
"""
    
    context.user_data["search_mode"] = True
    
    await update.callback_query.edit_message_text(
        search_instructions,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отменить поиск", callback_data="back_menu")]
        ])
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка поискового запроса"""
    if not update.message or not context.user_data.get("search_mode"):
        return
    
    search_query = update.message.text.strip().lower()
    context.user_data["search_mode"] = False
    
    data = load_all_data()
    results = []
    
    # Ищем по всем пользователям
    for user_id_str, user_info in data.get("users", {}).items():
        name = user_info.get("name", "").lower()
        username = user_info.get("username", "").lower()
        
        if (search_query in name or 
            search_query in username or 
            (search_query.startswith("@") and search_query[1:] in username)):
            
            # Находим комнаты пользователя
            user_rooms = []
            for code, room in data.get("rooms", {}).items():
                if user_id_str in room.get("members", {}):
                    room_status = "активна" if room.get("game_started") else "ожидание"
                    user_rooms.append(f"{code} ({room_status})")
            
            results.append({
                "id": user_id_str,
                "name": user_info.get("name", "Неизвестно"),
                "username": user_info.get("username", "без username"),
                "rooms": user_rooms,
                "quiz_points": user_info.get("quiz_points", 0),
                "grinch_wins": user_info.get("grinch_wins", 0)
            })
    
    # Формируем результат
    if not results:
        result_text = f"🔍 <b>По запросу '{search_query}' ничего не найдено.</b>"
    else:
        result_text = f"🔍 <b>Результаты поиска '{search_query}':</b>\n\n"
        
        for i, user in enumerate(results, 1):
            username_display = f"@{user['username']}" if user['username'] and user['username'] != "без username" else "без username"
            rooms_display = ", ".join(user['rooms']) if user['rooms'] else "нет активных комнат"
            
            result_text += f"<b>{i}. {user['name']}</b> ({username_display})\n"
            result_text += f"   ID: {user['id']}\n"
            result_text += f"   Комнаты: {rooms_display}\n"
            result_text += f"   🎓 Очков в квизе: {user['quiz_points']}\n"
            result_text += f"   ⚔️ Побед над Гринчем: {user['grinch_wins']}\n\n"
    
    admin = is_admin(update)
    await update.message.reply_text(
        result_text,
        parse_mode='HTML',
        reply_markup=enhanced_menu_keyboard(admin)
    )

# -------------------------------------------------------------------
# 🆕 ОБНОВЛЕННОЕ ГЛАВНОЕ МЕНЮ ДЛЯ АДМИНА
# -------------------------------------------------------------------
def enhanced_menu_keyboard(admin=False):
    base = [
        [InlineKeyboardButton("🎁 Ввести пожелание", callback_data="wish")],
        [InlineKeyboardButton("🎮 Мини-игры", callback_data="mini_games"),
         InlineKeyboardButton("🎁 Идеи подарков", callback_data="gift_ideas_menu")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("📋 Участники комнаты", callback_data="room_members")],
        [InlineKeyboardButton("🎅 Присоединиться к комнате", callback_data="join_room_menu")],
    ]
    
    # Добавляем кнопки админа
    if admin:
        base.append([InlineKeyboardButton("🏠 СОЗДАТЬ КОМНАТУ", callback_data="create_room_btn")])
        base.extend([
            [InlineKeyboardButton("📊 Админ: Распределение", callback_data="admin_view_distribution_menu")],
            [InlineKeyboardButton("🔍 Админ: Поиск пользователя", callback_data="admin_search_user")],
            [InlineKeyboardButton("🎄 Админ: Комнаты", callback_data="admin_rooms")],
            [InlineKeyboardButton("🚀 Админ: Запуск игры", callback_data="admin_start")],
            [InlineKeyboardButton("🗑️ Админ: Удалить комнату", callback_data="admin_delete")],
            [InlineKeyboardButton("📢 Админ: Рассылка", callback_data="broadcast_menu")],
            [InlineKeyboardButton("📈 Админ: Статистика", callback_data="admin_stats")],
        ])
    
    return InlineKeyboardMarkup(base)
    
# -------------------------------------------------------------------
# 📢 РАССЫЛКА
# -------------------------------------------------------------------
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    broadcast_info = """
📢 <b>Рассылка сообщений</b>

Выбери тип рассылки:

1. <b>Всем пользователям</b> - всем, кто когда-либо использовал бота
2. <b>Участникам комнат</b> - только тем, кто в активных комнатах

💡 <b>Совет:</b> Используй рассылку для важных объявлений или поздравлений!
"""
    
    keyboard = [
        [InlineKeyboardButton("👥 Всем пользователям", callback_data="broadcast_all")],
        [InlineKeyboardButton("🏠 Участникам комнат", callback_data="broadcast_rooms")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_menu")]
    ]
    
    await update.callback_query.edit_message_text(
        broadcast_info,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def broadcast_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
        return
    
    await update.callback_query.answer()
    
    context.user_data["broadcast_mode"] = "all"
    
    await update.callback_query.edit_message_text(
        "📢 <b>Рассылка всем пользователям</b>\n\n"
        "Напиши сообщение, которое будет отправлено всем пользователям бота:\n\n"
        "<i>💡 Форматирование HTML доступно</i>",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Отменить", callback_data="broadcast_cancel")]
        ])
    )

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    
    message = update.message.text
    broadcast_mode = context.user_data.get("broadcast_mode")
    
    if not broadcast_mode:
        return
    
    # Отправляем сообщение о начале рассылки
    progress_msg = await update.message.reply_text("📤 Начинаю рассылку...")
    
    sent_count = 0
    failed_count = 0
    
    if broadcast_mode == "all":
        # Рассылка всем пользователям
        for user_id in user_data.keys():
            try:
                await context.bot.send_message(
                    int(user_id),
                    f"📢 <b>Объявление от администратора:</b>\n\n{message}",
                    parse_mode='HTML'
                )
                sent_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                failed_count += 1
                print(f"Ошибка отправки пользователю {user_id}: {e}")
    
    elif broadcast_mode == "rooms":
        # Рассылка участникам комнат
        data = load_all_data()
        sent_users = set()
        
        for code, room in data["rooms"].items():
            for user_id in room["members"].keys():
                if user_id not in sent_users:
                    try:
                        await context.bot.send_message(
                            int(user_id),
                            f"📢 <b>Объявление для участников Тайного Санты:</b>\n\n{message}",
                            parse_mode='HTML'
                        )
                        sent_count += 1
                        sent_users.add(user_id)
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        failed_count += 1
                        print(f"Ошибка отправки пользователю {user_id}: {e}")
    
    # Удаляем режим рассылки
    if "broadcast_mode" in context.user_data:
        del context.user_data["broadcast_mode"]
    
    # Обновляем сообщение о прогрессе
    await progress_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📤 Отправлено: {sent_count}\n"
        f"❌ Не отправлено: {failed_count}\n\n"
        f"Сообщение доставлено получателям.",
        parse_mode='HTML'
    )
    
    admin = is_admin(update)
    await asyncio.sleep(3)
    await update.message.reply_text(
        "Выбери следующее действие:",
        reply_markup=enhanced_menu_keyboard(admin)
    )

async def broadcast_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "broadcast_mode" in context.user_data:
        del context.user_data["broadcast_mode"]
    
    await update.callback_query.edit_message_text(
        "❌ Рассылка отменена.",
        reply_markup=back_to_menu_keyboard(True)
    )

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
        # 🔥 Очищаем режимы при ЛЮБОМ callback (кроме wish_mode)
        if q.data != "wish":
            context.user_data["wish_mode"] = False
        if q.data != "join_room_menu":
            context.user_data["join_mode"] = False
        context.user_data["search_mode"] = False
        
        # Основные команды меню
        if q.data == "wish":
            await wish_start(update, context)
            
        elif q.data == "wish_cancel":  # <-- Добавьте этот обработчик
            context.user_data["wish_mode"] = False
            admin = is_admin(update)
            await q.edit_message_text(
                "❌ Ввод пожелания отменен.",
                reply_markup=enhanced_menu_keyboard(admin)
            )
            
        elif q.data == "wish_examples":
            await wish_examples(update, context)
            
        elif q.data == "gift_ideas_menu":
            await gift_ideas_menu(update, context)
            
        elif q.data == "gift_basic":
            idea = generate_gift_idea()
            await q.edit_message_text(
                f"🎁 <b>Базовая идея подарка:</b>\n\n{idea}\n\n"
                f"💡 <b>Совет:</b> учитывай интересы получателя!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Другая базовая идея", callback_data="gift_basic")],
                    [InlineKeyboardButton("🎁 Другие типы идей", callback_data="gift_ideas_menu")],
                    [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
                ])
            )
        
        elif q.data == "wish_cancel":  # <-- ДОБАВЬ ЭТОТ ОБРАБОТЧИК
            context.user_data["wish_mode"] = False
            admin = is_admin(update)
            await q.edit_message_text(
                "❌ Ввод пожелания отменен.",
                reply_markup=enhanced_menu_keyboard(admin)
            )    
        
        elif q.data == "admin_view_distribution_menu":
            await admin_view_distribution_menu(update, context)
            
        elif q.data.startswith("view_dist_"):
            await admin_view_distribution(update, context)
            
        elif q.data.startswith("reset_game_"):
            await admin_reset_game(update, context)
            
        elif q.data.startswith("export_room_"):
            await admin_export_room(update, context)
            
        elif q.data == "admin_search_user":
            await admin_search_user(update, context)
            
        elif q.data.startswith("gift_theme_"):
            theme = q.data.replace("gift_theme_", "")
            if theme == "random":
                themes = ["романтический", "деловой", "детский", "эко", "гастрономический", "спортивный", "творческий"]
                theme = random.choice(themes)
            
            ideas = gift_ideas_by_theme(theme, 3)
            text = f"🎪 <b>Идеи по тематике: {theme.upper()}</b>\n\n"
            for i, idea in enumerate(ideas, 1):
                text += f"<b>Идея {i}:</b>\n{idea}\n"
                if i != len(ideas):
                    text += "─" * 30 + "\n"
            
            await q.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"🔄 Другие {theme} идеи", callback_data=f"gift_theme_{theme}")],
                    [InlineKeyboardButton("🎪 Выбрать другую тему", callback_data="gift_themes_menu")],
                    [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
                ])
            )

        elif q.data == "gift_themes_menu":
            await gift_themes_menu(update, context)
            
        elif q.data.startswith("gift_emergency_"):
            if "today" in q.data or "tomorrow" in q.data or "week" in q.data:
                if "today" in q.data:
                    time_limit = "сегодня"
                elif "tomorrow" in q.data:
                    time_limit = "завтра"
                else:
                    time_limit = "неделя"
                budget = 2000
                idea = emergency_gift_idea(budget, time_limit)
            else:
                if "2000" in q.data:
                    budget = 2000
                elif "3000" in q.data:
                    budget = 3000
                elif "5000" in q.data:
                    budget = 5000
                else:
                    budget = 2000
                    time_limit = "сегодня"
                    idea = emergency_gift_idea(budget, time_limit)
            
            await q.edit_message_text(
                f"{idea}\n\n"
                f"💡 <b>Совет:</b> Добавь открытку с теплыми словами!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔥 Другие срочные идеи", callback_data="gift_emergency_random")],
                    [InlineKeyboardButton("🎁 Другие типы идей", callback_data="gift_ideas_menu")],
                    [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
                ])
            )

        elif q.data == "gift_emergency_menu":
            await gift_emergency_menu(update, context)
            
        elif q.data == "gift_emergency_random":
            budget = random.choice([1000, 2000, 3000, 5000])
            time_limit = random.choice(["сегодня", "завтра", "неделя"])
            idea = emergency_gift_idea(budget, time_limit)
            await q.edit_message_text(
                f"{idea}\n\n"
                f"💡 <b>Совет:</b> Не забудь про красивую упаковку!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔥 Другая срочная идея", callback_data="gift_emergency_random")],
                    [InlineKeyboardButton("🎁 Другие типы идей", callback_data="gift_ideas_menu")],
                    [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
                ])
            )

        elif q.data == "gift_combinations":
            combo = get_gift_combinations()
            await q.edit_message_text(
                f"{combo}\n\n"
                f"💡 <b>Совет:</b> Можно заменить любой элемент в наборе на аналогичный!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎨 Другой набор", callback_data="gift_combinations")],
                    [InlineKeyboardButton("🎁 Другие типы идей", callback_data="gift_ideas_menu")],
                    [InlineKeyboardButton("⬅️ В меню", callback_data="back_menu")]
                ])
            )
            
        elif q.data == "admin_rooms":
            if not is_admin(update): 
                await q.answer("🚫 Только администратор может просматривать комнаты", show_alert=True)
                return
            data = load_all_data()
            txt = "📦 <b>Созданные комнаты:</b>\n\n"
            if not data["rooms"]:
                txt += "Комнат пока нет. Создай первую комнату!"
            else:
                for c, room in data["rooms"].items():
                    status = "✅ Запущена" if room["game_started"] else "⏳ Ожидание"
                    txt += f"• <code>{c}</code> — {len(room['members'])} участников — {status}\n"
            await q.edit_message_text(
                txt, 
                parse_mode='HTML',
                reply_markup=back_to_menu_keyboard(True)
            )
            
        elif q.data == "admin_delete":
            await delete_room_menu(update, context)
            
        elif q.data.startswith("delete_"):
            await delete_specific_room(update, context)
            
        elif q.data == "admin_start":
            await start_game_admin(update, context)
            
        elif q.data == "admin_stats":
            await admin_statistics(update, context)
            
        elif q.data.startswith("start_"):
            await start_specific_game(update, context)
            
        elif q.data == "profile":
            await enhanced_profile(update, context)
            
        elif q.data == "quiz_top":
            await show_quiz_top(update, context)

        elif q.data == "quiz_finish_now":
            await finish_quiz(update, context)        
        
        elif q.data == "room_members":
            await show_room_members(update, context)
            
        elif q.data.startswith("room_members_"):
            await show_specific_room_members(update, context)
            
        elif q.data == "mini_games":
            await mini_game_menu(update, context)
            
        elif q.data == "join_room_menu":
            await join_room_menu(update, context)
            
        elif q.data == "room_help":
            await room_help(update, context)
            
        elif q.data == "broadcast_menu":
            await broadcast_menu(update, context)
            
        elif q.data == "broadcast_all":
            await broadcast_all_users(update, context)
            
        elif q.data == "broadcast_rooms":
            await broadcast_all_users(update, context)
            
        elif q.data == "broadcast_cancel":
            await broadcast_cancel(update, context)
            
        elif q.data == "create_room_btn":
            if not is_admin(update):
                await q.answer("🚫 Только администратор может создавать комнаты!", show_alert=True)
                return
            await create_room(update, context)
            
        elif q.data == "back_menu":
            # 🔥 ВАЖНО: Очищаем все режимы при возврате в меню
            context.user_data["wish_mode"] = False
            context.user_data["join_mode"] = False
            context.user_data["search_mode"] = False
            
            admin = is_admin(update)
            await q.edit_message_text(
                "🎄 Возвращаемся в главное меню...",
                reply_markup=enhanced_menu_keyboard(admin)
            )
            
        else:
            # Обработка игровых callback'ов
            await game_handlers(update, context)
        
        
    except Exception as e:
        print(f"Ошибка в обработчике callback: {e}")
        import traceback
        traceback.print_exc()
        await q.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)

# -------------------------------------------------------------------
# 🚀 ЗАПУСК БОТА
# -------------------------------------------------------------------
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Ошибка: {context.error}")
    try:
        if update and update.callback_query:
            await update.callback_query.answer("❌ Произошла ошибка!", show_alert=True)
    except:
        pass

def main():
    print("🎄 Инициализация бота Тайный Санта...")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    # Обработчики callback'ов
    application.add_handler(CallbackQueryHandler(enhanced_inline_handler))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    print("✅ Бот запущен и готов к работе!")
    print("🎅 Используйте /start для начала")
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()