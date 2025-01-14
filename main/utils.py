from datetime import datetime

import requests
from bs4 import BeautifulSoup


def clean_html_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def format_publication_date(published_at):
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]

    pub_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z")

    return f"{pub_date.day} {months[pub_date.month - 1]} {pub_date.year} года в {pub_date.strftime('%H:%M')}"


def get_exchange_rate(currency):
    if currency == 'RUR' or currency == 'RUB':
        return 1
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()

    if currency in data['Valute']:
        rate = data['Valute'][currency]['Value'] / data['Valute'][currency]['Nominal']
        return rate
    return None


def convert_to_rub(amount, currency):
    rate = get_exchange_rate(currency)
    if rate:
        return amount * rate
    else:
        return None


def convert_salary(salary):
    salary_from = salary['from']
    salary_to = salary['to']
    currency = salary['currency']

    salary_from_rub = None
    salary_to_rub = None

    if salary_from:
        salary_from_rub = convert_to_rub(salary_from, currency)
        if salary_from_rub:
            salary_from_rub = round(salary_from_rub, 2)

    if salary_to:
        salary_to_rub = convert_to_rub(salary_to, currency)
        if salary_to_rub:
            salary_to_rub = round(salary_to_rub, 2)

    return {'from': salary_from_rub, 'to': salary_to_rub, 'currency': 'RUB'}
