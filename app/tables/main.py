import pygsheets
from pygsheets import Spreadsheet, Worksheet


def get_table(table_id: str) -> Spreadsheet:
    client = pygsheets.authorize(service_account_file='app/tables/creds.json')
    return client.open_by_key(table_id)


def get_worksheets(table: Spreadsheet) -> list[Worksheet]:
    return table.worksheets()
