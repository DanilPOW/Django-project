import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"
TOTAL_VACANCIES = 6915298  # Общее количество вакансий


def process_data(df):
    # Подсчет количества вакансий по городам
    city_vacancy_count = df.groupby('area_name')['name'].count().reset_index(name='vacancy_count')
    return city_vacancy_count


def analyze_city_data(df):
    # Считаем общее количество вакансий по городам
    total_city_vacancies = df.groupby('area_name')['vacancy_count'].sum().reset_index()

    # Фильтруем города, где количество вакансий больше порога
    df_filtered = total_city_vacancies[total_city_vacancies['vacancy_count'] > 69153].copy()

    # Считаем долю вакансий от общего числа
    df_filtered['vacancy_share'] = df_filtered['vacancy_count'] / TOTAL_VACANCIES

    # Учет оставшихся данных в категории "Другие", если сумма долей < 1
    if df_filtered['vacancy_share'].sum() < 1:
        other_share = 1 - df_filtered['vacancy_share'].sum()
        other_row = pd.DataFrame({'area_name': ['Другие'], 'vacancy_share': [other_share]})
        df_filtered = pd.concat([df_filtered, other_row], ignore_index=True)

    # Сортировка по доле вакансий и выбор топ-10 городов
    df_top10 = df_filtered.sort_values(by='vacancy_share', ascending=False).head(10)

    return df_top10[['area_name', 'vacancy_share']]  # Возвращаем только нужные столбцы


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
        df_combined = pd.DataFrame()  # Для объединения данных по городам
        for future in futures:
            chunk_data = future.result()
            df_combined = pd.concat([df_combined, chunk_data], ignore_index=True)

    # Анализ данных по городам
    filtered_city_data = analyze_city_data(df_combined)

    # Сохранение сгруппированных данных в HTML
    grouped_df_to_html(filtered_city_data)

    # Подготовка данных для графиков по городам
    cities = list(filtered_city_data['area_name'])
    shares = list(filtered_city_data['vacancy_share'])

    return cities, shares


def grouped_df_to_html(grouped_df):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_string = grouped_df.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/city_vacancy_android.html', 'w', encoding='utf-8-sig') as f:
        f.write(html_string)

    return html_string


if "__main__" == __name__:
    # Получение данных для построения графиков
    cities, counts = create_report()  # Предполагается, что create_report возвращает два списка: города и количество вакансий

    # Создание фигуры с заданным размером
    plt.figure(figsize=(12, 8))  # Установка размера фигуры: ширина 12 дюймов, высота 8 дюймов

    # График доли вакансий по городам
    plt.pie(counts, labels=cities, autopct='%1.1f%%',
            textprops={'fontsize': 14})  # Добавлен параметр autopct для отображения процентов
    plt.title('Доля вакансий по городам', fontsize=24)  # Установка заголовка с размером шрифта

    # Сохранение графика в файл
    plt.savefig('./cache/city_vacancy_android.png')
