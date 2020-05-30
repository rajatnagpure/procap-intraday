import bs4
from constants import *
import requests


def get_specific_call(company_name):
    data = requests.post(TableURL, data={'intraMain': 2})
    soup = bs4.BeautifulSoup(data.content, 'lxml')
    table = soup.table
    table_rows = table.find_all('tr')
    tr = table_rows[1]
    table_rows = table_rows[1:]
    for trs in table_rows:
        all_tds = trs.find_all('td')[2].text
        if all_tds.find(company_name) != -1:
            tr = trs
    td = tr.find_all('td')
    row = [i.text for i in td]
    return row


def get_call():
    data = requests.post(TableURL, data={'intraMain': 2})
    soup = bs4.BeautifulSoup(data.content, 'lxml')
    table = soup.table
    table_rows = table.find_all('tr')
    tr = table_rows[1]
    td = tr.find_all('td')
    row = [i.text for i in td]
    return row[:-2]
