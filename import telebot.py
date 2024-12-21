import telebot
import requests
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Вставьте токен вашего бота
TOKEN = '7666309174:AAFjvARXjuwd0Hdm-0ZQI6ziafN1umo37GI'
bot = telebot.TeleBot(TOKEN)

# URL для AniList GraphQL API
ANILIST_API_URL = "https://graphql.anilist.co"

# Создаем или подключаемся к базе данных
conn = sqlite3.connect('user_data.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения списков пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_lists (
    user_id INTEGER,
    list_name TEXT,
    anime_name TEXT
)
''')
conn.commit()

# GraphQL запрос для получения топ-30 по рейтингу
def get_top30_by_rating():
    query = '''
    {
      Page(perPage: 30) {
        media(sort: SCORE_DESC) {
          title {
            romaji
            english
            native
          }
          averageScore
        }
      }
    }
    '''
    response = requests.post(ANILIST_API_URL, json={'query': query})
    if response.status_code == 200:
        data = response.json()
        return data['data']['Page']['media']
    else:
        print(f"Ошибка при запросе к AniList API: {response.status_code}")
        return []

# GraphQL запрос для получения топ-30 по популярности
def get_top30_by_popularity():
    query = '''
    {
      Page(perPage: 30) {
        media(sort: POPULARITY_DESC) {
          title {
            romaji
            english
            native
          }
          popularity
        }
      }
    }
    '''
    response = requests.post(ANILIST_API_URL, json={'query': query})
    if response.status_code == 200:
        data = response.json()
        return data['data']['Page']['media']
    else:
        print(f"Ошибка при запросе к AniList API: {response.status_code}")
        return []

# Поиск аниме по названию
def search_by_name(name):
    query = '''
    query ($name: String) {
      Page(perPage: 10) {
        media(search: $name) {
          title {
            romaji
            english
            native
          }
          averageScore
        }
      }
    }
    '''
    variables = {'name': name}
    response = requests.post(ANILIST_API_URL, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        data = response.json()
        return data['data']['Page']['media']
    else:
        print(f"Ошибка при запросе к AniList API: {response.status_code}")
        return []

# Поиск аниме по жанру
def search_by_genre(genre):
    query = '''
    query ($genre: String) {
      Page(perPage: 10) {
        media(genre: $genre) {
          title {
            romaji
            english
            native
          }
          averageScore
        }
      }
    }
    '''
    variables = {'genre': genre}
    response = requests.post(ANILIST_API_URL, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        data = response.json()
        return data['data']['Page']['media']
    else:
        print(f"Ошибка при запросе к AniList API: {response.status_code}")
        return []

# Кнопки для выбора настроения
def mood_buttons():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("Романтика"),
        KeyboardButton("Экшен"),
        KeyboardButton("Мрачное"),
        KeyboardButton("Веселое")
    )
    return markup

# Поиск рекомендаций по настроению с использованием genre
def get_recommendations_by_mood(mood):
    # Карта настроений на реальные жанры
    mood_to_genre = {
        "романтика": "Romance",
        "экшен": "Action",
        "мрачное": "Drama",
        "веселое": "Comedy"
    }
    genre = mood_to_genre.get(mood.lower())
    if not genre:
        return None

    query = '''
    query ($genre: String) {
      Page(perPage: 10) {
        media(genre: $genre, sort: SCORE_DESC) {
          title {
            romaji
            english
            native
          }
          averageScore
        }
      }
    }
    '''
    variables = {'genre': genre}
    response = requests.post(ANILIST_API_URL, json={'query': query, 'variables': variables})
    
    if response.status_code == 200:
        data = response.json()
        # Лог пустого ответа
        if not data['data']['Page']['media']:
            print(f"Пустой результат для жанра '{genre}'")
        return data['data']['Page']['media']
    else:
        print(f"Ошибка при запросе к AniList API: {response.status_code}, {response.text}")
        return []


# Работа с пользовательскими списками
def add_to_user_list(user_id, list_name, anime_name):
    cursor.execute('INSERT INTO user_lists (user_id, list_name, anime_name) VALUES (?, ?, ?)',
                   (user_id, list_name, anime_name))
    conn.commit()
    return True

def get_user_list(user_id, list_name):
    cursor.execute('SELECT anime_name FROM user_lists WHERE user_id = ? AND list_name = ?', (user_id, list_name))
    return [row[0] for row in cursor.fetchall()]





# Декоратор команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который поможет найти аниме по названию, жанру или настроению. Используй команды:\n"
                          "/recommend - рекомендации по настроению\n"
                          "/search_by_name <название> - поиск по названию\n"
                          "/search_by_genre <жанр> - поиск по жанру\n"
                          "/top30 - топ-30 аниме по рейтингу\n"
                          "/most_popular - топ-30 аниме по популярности\n"
                          "/add_to_watched <название> - добавить в список просмотренных\n"
                          "/add_to_plan <название> - добавить в список 'Планирую посмотреть'\n"
                          "/list <watched/plan_to_watch> - показать ваш список",
                 reply_markup=mood_buttons())

@bot.message_handler(commands=['recommend'])
def recommend_command(message):
    bot.reply_to(message, "Выберите настроение для рекомендаций:", reply_markup=mood_buttons())

# Обработчик для настроения
@bot.message_handler(func=lambda message: message.text in ["Романтика", "Экшен", "Мрачное", "Веселое"])
def handle_mood_selection(message):
    mood = message.text.lower()
    results = get_recommendations_by_mood(mood)
    if results:
        result_text = f"Рекомендации для настроения '{message.text}':\n"
        for anime in results:
            title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
            result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
        bot.reply_to(message, result_text)
    else:
        bot.reply_to(message, f"Не удалось найти рекомендации для настроения '{message.text}'. Попробуйте другое настроение!")

# Команда для добавления аниме в список "Просмотренные"
@bot.message_handler(commands=['add_to_watched'])
def add_to_watched(message):
    try:
        anime_name = message.text[len('/add_to_watched '):].strip()
        if not anime_name:
            bot.reply_to(message, "Пожалуйста, укажите название аниме для добавления в список просмотренных.")
            return
        user_id = message.from_user.id
        # Добавляем аниме в список "watched"
        if add_to_user_list(user_id, 'watched', anime_name):
            bot.reply_to(message, f"Аниме '{anime_name}' добавлено в ваш список 'Просмотренные'.")
        else:
            bot.reply_to(message, "Произошла ошибка при добавлении аниме в список 'Просмотренные'.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для добавления аниме в список "Планирую посмотреть"
@bot.message_handler(commands=['add_to_plan'])
def add_to_plan(message):
    try:
        anime_name = message.text[len('/add_to_plan '):].strip()
        if not anime_name:
            bot.reply_to(message, "Пожалуйста, укажите название аниме для добавления в список 'Планирую посмотреть'.")
            return
        user_id = message.from_user.id
        # Добавляем аниме в список "plan_to_watch"
        if add_to_user_list(user_id, 'plan_to_watch', anime_name):
            bot.reply_to(message, f"Аниме '{anime_name}' добавлено в ваш список 'Планирую посмотреть'.")
        else:
            bot.reply_to(message, "Произошла ошибка при добавлении аниме в список 'Планирую посмотреть'.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для вывода списка "Просмотренные" или "Планирую посмотреть"
@bot.message_handler(commands=['list'])
def list_anime(message):
    try:
        list_type = message.text[len('/list '):].strip().lower()
        if list_type not in ['watched', 'plan_to_watch']:
            bot.reply_to(message, "Пожалуйста, укажите правильный тип списка: 'watched' или 'plan_to_watch'.")
            return
        user_id = message.from_user.id
        user_list = get_user_list(user_id, list_type)
        if user_list:
            result_text = f"Ваш список '{list_type}':\n" + "\n".join(user_list)
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"Ваш список '{list_type}' пуст.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для поиска аниме по имени
@bot.message_handler(commands=['search_by_name'])
def search_by_name_command(message):
    try:
        name = message.text[len('/search_by_name '):].strip()
        if not name:
            bot.reply_to(message, "Пожалуйста, укажите название аниме для поиска.")
            return
        results = search_by_name(name)
        if results:
            result_text = f"Результаты поиска по названию '{name}':\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"Не удалось найти аниме по названию '{name}'.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для поиска аниме по жанру
@bot.message_handler(commands=['search_by_genre'])
def search_by_genre_command(message):
    try:
        genre = message.text[len('/search_by_genre '):].strip()
        if not genre:
            bot.reply_to(message, "Пожалуйста, укажите жанр для поиска.")
            return
        results = search_by_genre(genre)
        if results:
            result_text = f"Результаты поиска по жанру '{genre}':\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"Не удалось найти аниме по жанру '{genre}'.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для получения топ-30 по рейтингу
@bot.message_handler(commands=['top30'])
def top30_command(message):
    try:
        results = get_top30_by_rating()
        if results:
            result_text = "Топ-30 аниме по рейтингу:\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, "Не удалось получить топ-30 аниме по рейтингу.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда для получения топ-30 по популярности
@bot.message_handler(commands=['most_popular'])
def most_popular_command(message):
    try:
        results = get_top30_by_popularity()
        if results:
            result_text = "Топ-30 аниме по популярности:\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Популярность: {anime['popularity']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, "Не удалось получить топ-30 аниме по популярности.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Обработчик для неизвестных команд
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.reply_to(message, "Извините, я не понимаю эту команду. Попробуйте использовать одну из следующих команд:\n"
                          "/recommend - рекомендации по настроению\n"
                          "/search_by_name <название> - поиск по названию\n"
                          "/search_by_genre <жанр> - поиск по жанру\n"
                          "/top30 - топ-30 аниме по рейтингу\n"
                          "/most_popular - топ-30 аниме по популярности\n"
                          "/add_to_watched <название> - добавить в список просмотренных\n"
                          "/add_to_plan <название> - добавить в список 'Планирую посмотреть'\n"
                          "/list <watched/plan_to_watch> - показать ваш список")

# Запуск бота
bot.polling()
