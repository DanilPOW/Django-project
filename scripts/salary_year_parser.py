import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

file_path = "C:/Users/Daddy/Downloads/vacancies_2024.csv"
curr = './cache/currency.csv'
curr_csv = pd.read_csv(curr)


def extract_years_months(df):
    df['year'] = pd.to_datetime(df['published_at'], utc=True).dt.year.astype(str)
    df['month'] = pd.to_datetime(df['published_at'], utc=True).dt.month.astype(str)
    return df


def process_data(df):
    # Удаляем строки, где salary_currency null
    df = df.dropna(subset=['salary_currency']).copy()  # Убедитесь, что создается копия

    # Обрабатываем даты
    df = extract_years_months(df)

    # Вычисляем среднюю зарплату с помощью векторных операций
    salary_from = df['salary_from']
    salary_to = df['salary_to']

    # Используем np.where для вычисления средней зарплаты
    df['average_salary'] = np.where(
        salary_from.isna() & salary_to.isna(),  # Условие: оба поля null
        np.nan,  # Если оба поля null, устанавливаем значение NaN
        np.where(
            salary_from.isna(),  # Если salary_from null
            salary_to,  # Используем только salary_to
            np.where(
                salary_to.isna(),  # Если salary_to null
                salary_from,  # Используем только salary_from
                (salary_from + salary_to) / 2  # Если оба значения не null, вычисляем среднюю зарплату
            )
        )
    )

    # Удаляем строки с NaN в average_salary
    df = df.dropna(subset=['average_salary'])

    # Создаем столбец даты для конвертации валюты
    df['date'] = pd.to_datetime(df['month'] + '-' + df['year'], format='%m-%Y', errors='coerce')

    # Обработка конвертации валюты
    df['currency_rate'] = 1  # Установим значение по умолчанию для всех валют
    non_rur_mask = df['salary_currency'] != 'RUR'

    # Только для валют, отличных от 'RUR', получаем курсы из curr_csv
    df.loc[non_rur_mask, 'currency_rate'] = df.loc[non_rur_mask, 'date'].apply(
        lambda date: (
            curr_csv.loc[curr_csv['date'] == date, df.loc[non_rur_mask, 'salary_currency']].values[0]
            if not curr_csv.loc[curr_csv['date'] == date].empty and df.loc[non_rur_mask, 'salary_currency'].iloc[
                0] in curr_csv.columns
            else 1
        )
    )

    # Конвертируем среднюю зарплату в рубли
    df['average_salary'] *= df['currency_rate']

    # Удаляем зарплаты, превышающие 10 миллионов
    df = df[df['average_salary'] <= 10000000]

    # Группируем по годам и считаем среднюю зарплату
    return df.groupby('year')['average_salary'].mean().round(0).astype(int).to_dict()


def create_report():
    # Чтение данных целиком
    df = pd.read_csv(file_path, encoding='utf-8-sig')

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
        df_grouped = {}
        for future in futures:
            chunk_grouped = future.result()
            if chunk_grouped:  # Проверка, чтобы избежать ошибок при None
                for year, avg_salary in chunk_grouped.items():
                    if year in df_grouped:
                        df_grouped[year].append(avg_salary)
                    else:
                        df_grouped[year] = [avg_salary]

    # Подсчет средней зарплаты по годам
    df_grouped_avg = {year: np.mean(salaries) for year, salaries in df_grouped.items()}

    df_table = pd.DataFrame(list(df_grouped_avg.items()), columns=['Год', 'Средняя з/п'])

    grouped_df_to_html(df_table)

    # Подготовка данных для графиков
    years = list(df_grouped_avg.keys())
    avg_salary = list(df_grouped_avg.values())

    return years, avg_salary


def grouped_df_to_html(grouped_df):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_string = grouped_df.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/salary_year_anroid.html', 'w', encoding='utf-8') as f:
        f.write(html_string)

    return html_string


if "__main__" == __name__:
    # Получение данных для построения графиков
    year, salary = create_report()  # Предполагается, что create_report возвращает два списка: годы и зарплаты

    # Настройка осей
    x = np.arange(len(year))  # Позиции по оси X
    width = 0.35  # Ширина столбцов

    # Создание фигуры и подграфиков
    plt.figure(figsize=(12, 8))

    # График зарплат по годам
    plt.bar(x, salary, width, label='Средняя з/п')

    # Получение текущих осей
    ax = plt.gca()  # Получение текущих осей
    ax.set_title('Уровень зарплат по годам', fontsize=20)  # Установка заголовка
    ax.tick_params(axis='y', labelsize=12)  # Настройка размера меток по оси Y
    ax.set_xticks(x)  # Установка позиций по оси X
    ax.set_xticklabels(year, rotation=90, fontsize=12)  # Установка меток по оси X
    ax.legend(fontsize=12)  # Легенда
    ax.grid(True, axis='y')  # Сетка по оси Y

    plt.savefig('./cache/salary_year_android.png')
