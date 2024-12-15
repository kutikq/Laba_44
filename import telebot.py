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
print(df_cleaned.info())

# Просмотрите первые 5 строк
print(df.head())

# Декоратор команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Я тупой ботяра, не судите строго, напишем пару заметок(хз).")



# Запуск бота
bot.polling()