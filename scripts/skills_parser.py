import numpy as np
import pandas as pd
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

from matplotlib import pyplot as plt

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"


def process_data(df):
    df = df.copy()  # Убедитесь, что создается копия

    # Убираем строки, где key_skills - null
    df = df.dropna(subset=['key_skills'])

    # Подсчет навыков
    key_counter = Counter()
    df['key_skills'].str.split('\n').apply(key_counter.update)

    return key_counter


def create_report():
    # Чтение данных целиком
    df = pd.read_csv(file_path, dtype={1: str}, encoding='utf-8-sig')

    keywords = ['Android-разработчик', 'android', 'андроид', 'andorid', 'andoroid', 'andriod', 'andrind',
                          'xamarin']
    df = df[df['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    # Обработка данных в пуле процессов
    with ProcessPoolExecutor() as executor:
        # Разделяем DataFrame на несколько частей для параллельной обработки
        n_processes = 8  # Количество процессов
        df_split = np.array_split(df, n_processes)
        futures = [executor.submit(process_data, chunk) for chunk in df_split]

        # Собираем результаты
        total_key_counter = Counter()

        for future in futures:
            chunk_key_counter = future.result()
            total_key_counter.update(chunk_key_counter)

    # Получение топ-20 навыков
    top_skills = total_key_counter.most_common(20)

    # Подготовка данных для DataFrame
    df_table = pd.DataFrame(top_skills, columns=['Навык', 'Частота'])

    # Вызов функции для сохранения таблицы в HTML
    grouped_df_to_html(df_table)

    return df_table


def grouped_df_to_html(grouped_df):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_string = grouped_df.to_html(index=False, border=1, classes='dataframe', header=True)

    with open('./cache/top20_skills_android.html', 'w', encoding='utf-8-sig') as f:
        f.write(html_string)

    return html_string


if "__main__" == __name__:
    # Получение данных для построения отчета
    top_skills_df = create_report()

    plt.figure(figsize=(16, 10))
    plt.barh(top_skills_df['Навык'], top_skills_df['Частота'], color='skyblue')

    # Добавление заголовка и меток
    plt.title('ТОП-20 навыков', fontsize=24)
    plt.xlabel('Частота упоминаний', fontsize=14)
    plt.ylabel('Навык', fontsize=14)

    # Отображение графика
    plt.gca().invert_yaxis()  # Инвертируем ось Y, чтобы самый частый навык был сверху

    plt.tight_layout()
    plt.savefig('./cache/top20_skills_android.png')
