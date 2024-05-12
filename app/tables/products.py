import datetime as dt

from pygsheets import Worksheet

from app.tables.main import get_table, get_worksheets


def get_total_values(
    worksheet: Worksheet,
    total_cell_name: str
) -> list[int] | None:
    try:
        total_cell_row = worksheet.find(total_cell_name)[0].row
    except Exception:
        return

    raw_values = worksheet.get_row(
        total_cell_row,
        include_tailing_empty=False
    )[1::3]

    result = []
    for value in raw_values:
        value = value.replace('.', '').strip()

        if value.startswith('('):
            value = f'-{value[1:-1]}'

        result.append(int(value) if value.isnumeric() else 0)

    return result


def get_past_total_values(
    worksheets: list[Worksheet],
    delta: int,
    dates_col: int,
    current_date: dt.datetime = dt.datetime.now()
) -> list[int] | None:
    week_ago_date = dt.datetime.strftime(
        current_date - dt.timedelta(days=delta),
        format='%d.%m.%Y'
    )

    for worksheet in worksheets:
        worksheet_dates = worksheet.get_col(
            dates_col,
            include_tailing_empty=False
        )

        if week_ago_date not in worksheet_dates:
            continue

        row = worksheet_dates.index(week_ago_date) + 1
        raw_values = worksheet.get_row(
            row,
            include_tailing_empty=False
        )[1::3]

        break

    result = []
    for value in raw_values:
        value = value.replace('.', '').strip()

        if value.startswith('('):
            value = f'-{value[1:-1]}'

        result.append(int(value) if value.isnumeric() else 0)

    return result


def get_total_titles(
    worksheet: Worksheet,
    title_row: str
) -> list[str] | None:
    return worksheet.get_row(title_row, include_tailing_empty=False)[1::3]


def get_data(products_table_settings):
    table = get_table(products_table_settings['table_id'])
    worksheets = [
        w for w in get_worksheets(table)
        if w.title[-1] == products_table_settings['worksheet_postfix']
    ]

    data = zip(
        get_total_titles(
            worksheets[0],
            products_table_settings['title_row']
        ),
        get_total_values(
            worksheets[0],
            products_table_settings['total_cell_name']
        ),
        get_past_total_values(
            worksheets,
            products_table_settings['days_delta'],
            products_table_settings['date_col']
        )
    )

    return data


def get_minimal_total() -> int:
    return 500
