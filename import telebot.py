import telebot
import requests

# Вставьте токен вашего бота
TOKEN = '7666309174:AAFjvARXjuwd0Hdm-0ZQI6ziafN1umo37GI'
bot = telebot.TeleBot(TOKEN)

# URL для AniList GraphQL API
ANILIST_API_URL = "https://graphql.anilist.co"

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

# Декоратор команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может помочь найти аниме по названию или жанру. Используй команды:\n"
                          "/search_by_name <название> - поиск по названию\n"
                          "/search_by_genre <жанр> - поиск по жанру\n"
                          "/top30 - топ-30 аниме по рейтингу\n"
                          "/most_popular - топ-30 аниме по популярности")

# Обработчик команды /search_by_name
@bot.message_handler(commands=['search_by_name'])
def handle_search_by_name(message):
    query = message.text[len('/search_by_name '):]  # Извлекаем запрос после команды
    if query:
        results = search_by_name(query)
        if results:
            result_text = f"Найдено аниме по запросу '{query}':\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"По запросу '{query}' ничего не найдено.")
    else:
        bot.reply_to(message, "Пожалуйста, введите название аниме после команды /search_by_name.")

# Обработчик команды /search_by_genre
@bot.message_handler(commands=['search_by_genre'])
def handle_search_by_genre(message):
    query = message.text[len('/search_by_genre '):]  # Извлекаем запрос после команды
    if query:
        results = search_by_genre(query)
        if results:
            result_text = f"Найдено аниме по жанру '{query}':\n"
            for anime in results:
                title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
                result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"По запросу '{query}' ничего не найдено.")
    else:
        bot.reply_to(message, "Пожалуйста, введите жанр после команды /search_by_genre.")

# Обработчик команды /top30
@bot.message_handler(commands=['top30'])
def handle_top30(message):
    results = get_top30_by_rating()
    if results:
        result_text = "Топ 30 аниме по рейтингу:\n"
        for anime in results:
            title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
            result_text += f"{title} - Рейтинг: {anime['averageScore']}\n"
        bot.reply_to(message, result_text)
    else:
        bot.reply_to(message, "Не удалось получить данные для топ-30 по рейтингу.")

# Обработчик команды /most_popular
@bot.message_handler(commands=['most_popular'])
def handle_most_popular(message):
    results = get_top30_by_popularity()
    if results:
        result_text = "Топ 30 аниме по популярности:\n"
        for anime in results:
            title = anime['title']['romaji'] if anime['title']['romaji'] else anime['title']['english']
            result_text += f"{title} - Популярность: {anime['popularity']}\n"
        bot.reply_to(message, result_text)
    else:
        bot.reply_to(message, "Не удалось получить данные для топ-30 по популярности.")

# Обработчик для неизвестных команд
@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.reply_to(message, "Извините, я не понимаю эту команду. Попробуйте использовать одну из следующих команд:\n"
                          "/start - начать\n"
                          "/search_by_name <название> - поиск по названию\n"
                          "/search_by_genre <жанр> - поиск по жанру\n"
                          "/top30 - топ-30 аниме по рейтингу\n"
                          "/most_popular - топ-30 аниме по количеству зрителей")

# Запуск бота
bot.polling()
