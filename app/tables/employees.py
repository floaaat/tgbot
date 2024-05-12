import datetime

from pygsheets import Worksheet

from app.tables.main import get_table, get_worksheets


def get_dates(days_delta: int) -> list[str]:
    return [
        (
            datetime.datetime.now() - datetime.timedelta(days=i)
        ).strftime('%d/%m/%Y') for i in range(1, days_delta + 1)
    ]


def get_names(worksheet: Worksheet, employees_table_settings):
    return worksheet.get_col(
        employees_table_settings['employees_names_col'],
        include_tailing_empty=False
    )


def get_income_cols(worksheet: Worksheet, employees_table_settings):
    result = {}
    income_cols = employees_table_settings['income_cols']

    for country, income_col in income_cols.items():
        result[country] = worksheet.get_col(income_col)

    return result


def get_data(employees_table_settings):
    table = get_table(employees_table_settings['table_id'])
    print('TABLE: OK')
    dates = get_dates(employees_table_settings['days_delta'])
    print('DATES: OK')

    worksheets = [
        w for w in get_worksheets(table)
        if w.title in dates
    ]
    print('WORKSHEETS: OK')

    data = {}

    for worksheet in worksheets:
        names = get_names(worksheet, employees_table_settings)
        print(f'{worksheet.title} names: OK')

        income_cols = get_income_cols(
            worksheet,
            employees_table_settings
        )
        print(f'{worksheet.title} income_cols: OK')

        for index, name in enumerate(names):
            if any(
                word in name for word in employees_table_settings['skip_words']
            ):
                continue

            if name.endswith(' W') or name.endswith(' w'):
                name = name[:-2]

            for country, income_col in income_cols.items():
                income = float(
                    income_col[index][1:] if
                    income_col[index][1:].replace('.', '').isnumeric()
                    else 0
                )

                if income:
                    # print(f'{worksheet.title}: {name} - {income}')
                    if country in data:
                        if name in data[country]:
                            data[country][name].append(income)
                        else:
                            data[country][name] = [income]
                    else:
                        data[country] = {name: [income]}

    for country, country_data in data.items():
        for name, incomes in country_data.items():
            data[country][name] = sum(incomes) / len(incomes)

    return data


def get_minimal_income():
    return 60
