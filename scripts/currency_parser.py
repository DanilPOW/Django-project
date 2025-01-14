import pandas as pd

CURRENCIES = ["BYR", "USD", "EUR", "KZT", "UAH", "AZN", "KGS", "UZS", "GEL"]

start_date = pd.to_datetime('2003-01-01')
end_date = pd.to_datetime('2025-01-01')
range_dates = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%d/%m/%Y')


def collect(date_str):
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
    data = pd.read_xml(url, xpath=".//Valute", encoding="windows-1251")

    if data is not None and not data.empty:
        data['date'] = pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m')
        data = data[data['CharCode'].isin(CURRENCIES)]
        data['Value'] = pd.to_numeric(data['Value'].str.replace(',', '.'), errors='coerce')
        data['Nominal'] = pd.to_numeric(data['Nominal'], errors='coerce')
        data['normalized'] = round(data['Value'] / data['Nominal'], 9)

        return data[['date', 'CharCode', 'normalized']]

    return pd.DataFrame(columns=['date', 'CharCode', 'normalized'])


all_data = []
for i, date_str in enumerate(range_dates):
    df = collect(date_str)
    if not df.empty:
        all_data.append(df)

final_df = pd.concat(all_data, ignore_index=True)
pivot = final_df.pivot(index='date', columns='CharCode', values='normalized')
pivot = pivot[CURRENCIES]
pivot.to_csv("./cache/currency.csv")
