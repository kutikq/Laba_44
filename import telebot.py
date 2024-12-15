import telebot
import pandas as pd

# Вставьте токен вашего бота
TOKEN = '7666309174:AAFjvARXjuwd0Hdm-0ZQI6ziafN1umo37GI'
bot = telebot.TeleBot(TOKEN)

# Загрузите датасет
df = pd.read_csv('anime.csv')
# Удалить строки с пропущенными значениями
df_cleaned = df.dropna()

# Просмотрите первые 5 строк
print(df.head())

# Декоратор команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может помочь найти аниме по названию или жанру. Используй команды:\n"
                          "/search_by_name <название> - поиск по названию\n"
                          "/search_by_genre <жанр> - поиск по жанру\n"
                          "/top30 - топ-30 аниме по рейтингу\n"
                          "/most_popular - топ-30 аниме по количеству зрителей")

# Поиск по названию
def search_by_name(name):
    result = df_cleaned[df_cleaned['name'].str.contains(name, case=False, na=False)]
    return result

# Поиск по жанру
def search_by_genre(genre):
    result = df_cleaned[df_cleaned['genre'].str.contains(genre, case=False, na=False)]
    return result

# Вывод топ 30 по рейтингу
def show_top100_rait():
    top_30_r = df_cleaned.sort_values(by='rating', ascending=False)  # Сортировка по убыванию
    result = top_30_r.head(30)
    return result

# Топ 30 по зрителям
def show_most_popular():
    top_30_m = df_cleaned.sort_values(by='members', ascending=False)  # Сортировка по убыванию
    result = top_30_m.head(30)
    return result

# Обработчик команды /search_by_name
@bot.message_handler(commands=['search_by_name'])
def handle_search_by_name(message):
    query = message.text[len('/search_by_name '):]  # Извлекаем запрос после команды
    if query:
        results = search_by_name(query)
        if not results.empty:
            result_text = f"Найдено аниме по запросу '{query}':\n"
            for _, row in results.head(5).iterrows():  # Отображаем только первые 5 результатов
                result_text += f"{row['name']} - Рейтинг: {row['rating']}\n"
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
        if not results.empty:
            result_text = f"Найдено аниме по запросу '{query}':\n"
            for _, row in results.head(5).iterrows():  # Отображаем только первые 5 результатов
                result_text += f"{row['genre']} - Рейтинг: {row['rating']}\n"
            bot.reply_to(message, result_text)
        else:
            bot.reply_to(message, f"По запросу '{query}' ничего не найдено.")
    else:
        bot.reply_to(message, "Пожалуйста, введите жанр после команды /search_by_genre.")

# Обработчик команды /top30
@bot.message_handler(commands=['top30'])
def handle_top100(message):
    results = show_top100_rait()
    result_text = "Топ 30 аниме по рейтингу:\n"
    for _, row in results.iterrows():
        result_text += f"{row['name']} - Рейтинг: {row['rating']}\n"
    bot.reply_to(message, result_text)

# Обработчик команды /most_popular
@bot.message_handler(commands=['most_popular'])
def handle_most_popular(message):
    results = show_most_popular()
    result_text = "Топ 30 аниме по количеству зрителей:\n"
    for _, row in results.iterrows():
        result_text += f"{row['name']} - Зрители: {row['members']}\n"
    bot.reply_to(message, result_text)

# Запуск бота
bot.polling()
