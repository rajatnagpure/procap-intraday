import requests
import bs4
from constants import *
import json


def generate_mis_multiplier_dict():
    try:
        page = requests.get(margin_calculator_page_url)
        soup = bs4.BeautifulSoup(page.text, 'lxml')
        soup_whole_table = soup.find('table', attrs={'class': 'data equity', 'id': 'table'})
        soup_table = soup_whole_table.find('tbody')
        for row in soup_table.find_all('tr'):
            cols = row.find_all('td')
            script = cols[1].text
            script = script[:script.find(':')]
            mis_multi = int(cols[3].text.strip()[:-1])
            mis_multipliers[script] = mis_multi
        try:
            with open('mis_multi_dict.json','w') as json_file:
                json.dump(mis_multipliers,json_file)
        except Exception as e:
            logger.critical("Problem dumping MIS multiplier dict into json file")
    except Exception as e:
        logger.critical("problem generating MIS multiplier dictionary {}".format(e))
        print("problem generating MIS multiplier dictionary {}".format(e))
        generate_mis_multiplier_dict()
        return

