import requests
from kiteconnect import KiteConnect
from constants import *
import datetime
import json


def get_access_token():
    kite = KiteConnect(api_key=zerodha_api_key)
    url = kite.login_url()
    login = requests.get(url)
    cookies = ';'.join([f'{k}={v}' for k, v in login.history[1].cookies.items()])
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
        "X-Kite-Userid": zerodha_id, 'X-Kite-Version': '2.4.0',
        'Cookie': cookies, 'Referer': login.url
    }
    data = requests.post('https://kite.zerodha.com/api/login',
                         data={'user_id': zerodha_id, 'password': zerodha_password},
                         headers=headers)
    request_id = data.json()['data']['request_id']
    data = requests.post('https://kite.zerodha.com/api/twofa',
                         data={'user_id': zerodha_id, 'request_id': request_id, 'twofa_value': zerodha_pin},
                         headers=headers)
    # public_token = data.json()['data']['public_token']
    public_token = data.cookies.get_dict()['public_token']
    user_id = 'user_id=' + zerodha_id
    headers.update({'Cookie': cookies + ';' + 'public_token=' + public_token + ';' + user_id})
    data = requests.get(login.url + '&skip_session=true', headers=headers)
    request_token = data.url.split("?")[1].split("&")[0].split("=")[1]
    try:
        data = kite.generate_session(request_token, zerodha_api_secret)
    except Exception as e:
        logger.critical("Probelm generating access token: {}".format(e))
        get_access_token()
        return
    global zerodha_access_token
    zerodha_access_token = data["access_token"]
    logger.critical("Access Token {}".format(zerodha_access_token))
    at_dict = {}
    at_dict["access_token"] = zerodha_access_token
    at_dict["time"] = datetime.datetime.now().strftime("%m/%d/%Y")
    try:
        with open('access_token.json', 'w') as json_file:
            json.dump(at_dict, json_file)
    except Exception as e:
        logger.critical("Problem dumping access Token into json file")


def invalidate_access_token():
    kite = KiteConnect(api_key=zerodha_api_key)
    kite.set_access_token(zerodha_access_token)
    kite.invalidate_access_token(zerodha_access_token)


def get_company_name(close_match_list, order_price):
    kite = KiteConnect(api_key=zerodha_api_key)
    kite.set_access_token(zerodha_access_token)
    mini = 100
    my_stock = close_match_list[0]
    for i in close_match_list:
        q = abs(kite.ltp("NSE:" + i)["NSE:" + i]["last_price"] - order_price)
        if q < mini:
            mini = q
            my_stock = i
    return my_stock


def get_mis_buyable_quantity(stock_quote, order_price):
    global mis_multipliers
    kite = KiteConnect(api_key=zerodha_api_key)
    kite.set_access_token(zerodha_access_token)
    total_margin_available = kite.margins()["equity"]["net"]
    cnc_quantity = total_margin_available / order_price
    mis_multi = mis_multipliers[stock_quote]
    return int(cnc_quantity * mis_multi)


def place_bo_order(quote, action, quantity, order_price, target_price, stop_loss_price):
    kite = KiteConnect(api_key=zerodha_api_key)
    kite.set_access_token(zerodha_access_token)
    kite.place_order("bo",
                     "NSE",
                     quote,
                     action,
                     quantity,
                     "MIS",
                     "LIMIT",
                     price=order_price,
                     validity=None,
                     disclosed_quantity=None,
                     trigger_price=None,
                     squareoff=target_price,
                     stoploss=stop_loss_price,
                     trailing_stoploss=None,
                     tag=None)
