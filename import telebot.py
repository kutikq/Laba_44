import telebot
import requests
import json
import pandas as pd

# Вставьте токен вашего бота
TOKEN = '7666309174:AAFjvARXjuwd0Hdm-0ZQI6ziafN1umo37GI'
bot = telebot.TeleBot(TOKEN)

#API 
# Загрузите датасет
df = pd.read_csv('anime.csv')
# Удалить строки с пропущенными значениями
df_cleaned = df.dropna()

# Просмотрите первые 5 строк
print(df.head())

# Декоратор команды /start
@bot.message_handler(commands = ['start'])
def send_welcome(message):
    bot.reply_to(message, "Я тупой ботяра, не судите строго, напишем пару заметок(хз).")

# Поиск по названию
def search_by_name(name):
    result = df[df['name'].str.contains(name, case = False, na = False)]
    return result
# Поиск по жанру
def search_by_genre(genre):
    result = df[df['genre'].str.contains(genre, case = False, na = False)]
    return result

# Вывод топ 100 по популярности
def show_top100_rait():
    top_100 = df.sort_values(by = 'rating')
    result = top_100.head(100)
    return result

# Топ 100 по зрителям
def show_top100_rait():
    top_100 = df.sort_values(by = 'members')
    result = top_100.head(100)
    return result


# Запуск бота
bot.polling()