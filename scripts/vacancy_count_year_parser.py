import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"


def extract_years_months(df):
    df['year'] = pd.to_datetime(df['published_at'], utc=True).dt.year.astype(str)
    return df


def process_data(df):
    df = df.copy()  # Убедитесь, что создается копия
    df = extract_years_months(df)

    # Подсчет общего количества вакансий по годам
    vacancy_count = df.groupby('year')['name'].count().to_dict()

    return vacancy_count


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
        df_grouped_vacancy_count = {}

        for future in futures:
            chunk_vacancy_count = future.result()
            for year, count in chunk_vacancy_count.items():
                if year in df_grouped_vacancy_count:
                    df_grouped_vacancy_count[year] += count
                else:
                    df_grouped_vacancy_count[year] = count

    # Подготовка данных для HTML-таблицы
    df_table = pd.DataFrame(list(df_grouped_vacancy_count.items()), columns=['Год', 'Количество вакансий'])

    # Вызов функции для сохранения таблицы в HTML
    grouped_df_to_html(df_table)

    # Подготовка данных для графиков
    years = list(df_grouped_vacancy_count.keys())
    vacancy_counts = list(df_grouped_vacancy_count.values())

    return years, vacancy_counts


def grouped_df_to_html(grouped_df):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_string = grouped_df.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/vacancy_count_android.html', 'w', encoding='utf-8-sig') as f:
        f.write(html_string)

    return html_string


if "__main__" == __name__:
    # Получение данных для построения графиков
    year, count = create_report()  # Предполагается, что create_report возвращает два списка: год и количество

    # Настройка осей
    x = np.arange(len(year))  # Позиции по оси X
    width = 0.35  # Ширина столбцов

    # Создание фигуры и подграфиков
    plt.figure(figsize=(12, 8))

    # График количества вакансий по годам
    plt.bar(x, count, width, label='Количество вакансий')

    # Настройка заголовка и меток осей
    plt.title('Количество вакансий по годам', fontsize=16)
    plt.xticks(x, year, rotation=90, fontsize=10)  # Установка меток по оси X
    plt.legend(fontsize=10)
    plt.grid(True, axis='y')

    # Сохранение графика в файл
    plt.savefig('./cache/vacancy_count_android.png')
