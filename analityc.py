import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузите датасет
df = pd.read_csv('anime.csv')

# Удалить строки с пропущенными значениями
df_cleaned = df.dropna()

# Сортировка по количеству зрителей (топ-30)
top_30_m = df_cleaned.sort_values(by='members', ascending=False).head(30)

# Проверка корреляции между рейтингом и количеством зрителей
correlation = top_30_m['rating'].corr(top_30_m['members'])  # Корреляция между рейтингом и количеством зрителей
print(f"Корреляция между рейтингом и количеством зрителей (топ 30): {correlation}")

# Создаем диаграмму рассеяния
plt.figure(figsize=(10,6))
sns.scatterplot(data=top_30_m, x='members', y='rating', color='blue', alpha=0.6)

# Добавляем линию тренда с помощью регрессии
sns.regplot(data=top_30_m, x='members', y='rating', scatter=False, color='red', line_kws={'linewidth': 2})

# Добавляем названия аниме на график
for i in range(len(top_30_m)):
    plt.text(top_30_m['members'].iloc[i], top_30_m['rating'].iloc[i], top_30_m['name'].iloc[i], fontsize=8, ha='right', va='bottom', alpha=0.7)

# Настройки графика
plt.title('Корреляция между рейтингом и количеством зрителей (Топ 30 по зрителям)')
plt.xlabel('Количество зрителей')
plt.ylabel('Рейтинг')
plt.grid(True)

# Показываем график
plt.show()