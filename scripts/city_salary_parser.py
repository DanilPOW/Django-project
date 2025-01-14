from multiprocessing import Manager
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


def get_currency_rate(row):
    date = row['date']
    currency = row['salary_currency']

    # Проверяем, есть ли курс для данной даты и валюты
    if currency in curr_csv.columns:
        rate_row = curr_csv.loc[curr_csv['date'] == date]
        if not rate_row.empty:
            rate_value = rate_row[currency].values[0]
            # Проверяем, является ли значение null
            if pd.isnull(rate_value):
                return None
            return rate_value

    return 1  # Если курс не найден, возвращаем 1


def process_data(df):
    df = df.dropna(subset=['area_name']).copy()
    # Локальный словарь для подсчета вакансий в чанке
    vacancy_counter = {}
    # Подсчитываем количество вакансий для каждого города
    for area in df['area_name']:
        if area in vacancy_counter:
            vacancy_counter[area] += 1
        else:
            vacancy_counter[area] = 1

    df = df.dropna(subset=['salary_currency']).copy()  # Убедитесь, что создается копия
    df = extract_years_months(df)

    # Вычисляем среднюю зарплату с помощью векторных операций
    salary_from = df['salary_from']
    salary_to = df['salary_to']

    # Создаем столбец даты для конвертации валюты
    df['date'] = pd.to_datetime(df['month'] + '-' + df['year'], format='%m-%Y', errors='coerce')

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

    # Обработка конвертации валюты
    df['currency_rate'] = 1  # Установим значение по умолчанию для всех валют
    non_rur_mask = df['salary_currency'] != 'RUR'

    # Применяем функцию получения курсов валют
    df.loc[non_rur_mask, 'currency_rate'] = df[non_rur_mask].apply(get_currency_rate, axis=1)

    # Фильтруем строки, где currency_rate равно None
    df = df[df['currency_rate'].notnull()]

    # Конвертируем среднюю зарплату в рубли
    df['average_salary'] *= df['currency_rate']

    # Удаляем зарплаты, превышающие 10 миллионов
    df = df[df['average_salary'] <= 10000000]

    return df, vacancy_counter  # Возвращаем как данные, так и счетчик вакансий


def analyze_city_data(df, vacancy_counter):
    # Группируем данные по городам и считаем общую зарплату и количество вакансий
    salary_city = df.groupby('area_name').agg(mean_salary=('average_salary', 'mean')).reset_index()

    # Фильтруем города, где количество вакансий в vacancy_counter больше 69153
    salary_city = salary_city[salary_city['area_name'].apply(lambda x:
                                                             vacancy_counter[x] > 0.01 * sum(vacancy_counter.values()))]

    salary_city['mean_salary'] = salary_city['mean_salary'].round(0).astype(int)

    # Топ-10 по средней зарплате
    top_10_city_sal = salary_city.sort_values('mean_salary', ascending=False).head(10)

    return top_10_city_sal[['area_name', 'mean_salary']]


def create_report():
    # Чтение данных целиком
    df = pd.read_csv(file_path, dtype={1: str}, encoding='utf-8-sig')

    keywords = ['Android-разработчик', 'android', 'андроид', 'andorid', 'andoroid', 'andriod', 'andrind',
                          'xamarin']
    df = df[df['name'].str.contains('|'.join(keywords), case=False, na=False, regex=True)]

    # Используем Manager для совместного использования vacancy_counter
    manager = Manager()
    total_vacancy_counter = manager.dict()

    # Обработка данных в пуле процессов
    with ProcessPoolExecutor() as executor:
        # Разделяем DataFrame на несколько частей для параллельной обработки
        n_processes = 8  # Количество процессов
        df_split = np.array_split(df, n_processes)
        futures = [executor.submit(process_data, chunk) for chunk in df_split]

        # Собираем результаты
        df_combined = pd.DataFrame()  # Для объединения данных по городам
        for future in futures:
            chunk_data, chunk_vacancy_counter = future.result()
            df_combined = pd.concat([df_combined, chunk_data], ignore_index=True)

            # Объединяем локальные счетчики вакансий
            for area, count in chunk_vacancy_counter.items():
                if area in total_vacancy_counter:
                    total_vacancy_counter[area] += count
                else:
                    total_vacancy_counter[area] = count

    # Анализ данных по городам
    top_10_city_sal = analyze_city_data(df_combined, dict(total_vacancy_counter))

    # Сохранение сгруппированных данных в HTML
    grouped_df_to_html(top_10_city_sal)

    # Подготовка данных для графиков по городам
    cities = list(top_10_city_sal['area_name'])
    city_salaries = list(top_10_city_sal['mean_salary'])

    return cities, city_salaries


def grouped_df_to_html(grouped_df):
    # Преобразуем сгруппированный DataFrame в HTML-таблицу
    html_string = grouped_df.to_html(index=True, border=1, classes='dataframe', header=True)

    with open('./cache/city_salary_android.html', 'w', encoding='utf-8-sig') as f:
        f.write(html_string)

    return html_string


if "__main__" == __name__:
    # Получение данных для построения графиков
    cities, salary = create_report()  # Предполагается, что create_report возвращает два списка: города и зарплаты

    # Создание фигуры
    plt.figure(figsize=(12, 8))

    # График зарплат по городам
    plt.barh(cities, salary)
    plt.title('Уровень зарплат по городам', fontsize=20)  # Увеличен размер шрифта заголовка

    # Получение текущих осей и установка меток
    ax = plt.gca()  # Получение текущих осей
    for label in ax.get_yticklabels():
        label.set_ha('right')
        label.set_va('center')

    ax.invert_yaxis()
    plt.grid(True, axis='x')
    plt.tick_params(axis='y', labelsize=10)  # Увеличен размер шрифта для меток по оси Y
    plt.tick_params(axis='x', labelsize=12)  # Увеличен размер шрифта для меток по оси X

    plt.savefig('./cache/city_salary_android.png')
