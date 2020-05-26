from extractvalues import *
import datetime
from time import sleep
import copy
from browser import *
from kiteconnect import KiteConnect
import generateMISMultiplierDict
import requests
import json
from constants import *


# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------ZERODHA UTILS-------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #


def get_access_token():
    global kite
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
    kite.invalidate_access_token(zerodha_access_token)


def get_company_quote(close_match_list, order_price):
    mini = 100
    my_stock = close_match_list[0]
    for i in close_match_list:
        q = abs(kite.ltp("NSE:" + i)["NSE:" + i]["last_price"] - order_price)
        if q < mini:
            mini = q
            my_stock = i
    return my_stock


def get_mis_buyable_quantity(stock_quote, order_price):
    total_margin_available = kite.margins()["equity"]["net"]
    cnc_quantity = total_margin_available / order_price
    mis_multi = mis_multipliers[stock_quote]
    return int(cnc_quantity * mis_multi)


def place_bo_order(order_detail):
    action = order_detail["action"]
    order_price = order_detail["order_price"]
    target_price = order_detail["target_price"]
    stop_loss_price = order_detail["stop_loss_price"]
    stock_quote = get_company_quote(order_detail["close_match_list"])
    quantity = get_mis_buyable_quantity(stock_quote, order_price)
    try:
        kite.place_order(kite.VARIETY_BO,
                         kite.EXCHANGE_NSE,
                         stock_quote,
                         action,
                         quantity,
                         kite.PRODUCT_MIS,
                         kite.ORDER_TYPE_LIMIT,
                         price=order_price,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=target_price,
                         stoploss=stop_loss_price,
                         trailing_stoploss=None,
                         tag=None)
    except Exception as e:
        logger.critical("Problem Placing order: {}".format(e))
        place_bo_order(order_detail)
    # now looping for exit check


def place_co_order(order_detail):
    action = order_detail["action"]
    order_price = order_detail["order_price"]
    target_price = order_detail["target_price"]
    stop_loss_price = order_detail["stop_loss_price"]
    stock_quote = get_company_quote(order_detail["close_match_list"])
    quantity = get_mis_buyable_quantity(stock_quote, order_price)
    try:
        kite.place_order(kite.VARIETY_CO,
                         kite.EXCHANGE_NSE,
                         stock_quote,
                         action,
                         quantity,
                         kite.PRODUCT_MIS,
                         kite.ORDER_TYPE_LIMIT,
                         price=order_price,
                         validity=None,
                         disclosed_quantity=None,
                         trigger_price=None,
                         squareoff=None,
                         stoploss=stop_loss_price,
                         trailing_stoploss=None,
                         tag=None)
    except Exception as e:
        logger.critical("Problem Placing order: {}".format(e))
        place_bo_order(order_detail)
    # now looping for exit check



# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------ZERODHA UTILS ENDS--------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #



def start():
    global procap
    # list and calls
    curr_list = procap.get_call()
    prev_list = copy.deepcopy(curr_list)
    new_call = extractValues(curr_list)
    logger.critical(curr_list)
    logger.critical(new_call.get_call_dict())

    refresh_count = 0

    while datetime.datetime.now().time() < market_opening_time:
        sleep(1)
    print('started')
    while 1:
        sleep(2)
        # refresh list
        try:
            curr_list = procap.get_call()
        except Exception as e:
            logger.critical("Exception while refreshing call : " + e.__str__())
            procap.stop_browser()
            sleep(500)
            logger.critical("starting browser again")
            start()
            return

        refresh_count = refresh_count + 1
        if curr_list == prev_list:
            logger.critical('getting pass')
        else:
            try:
                new_call.reuse(curr_list)
            except Exception as e:
                logger.critical("Exception while extracting call : " + e.__str__())
                prev_list = copy.deepcopy(curr_list)
                continue

            tle = (datetime.datetime.combine(datetime.datetime.now(), datetime.datetime.now().time()) - datetime.datetime.combine(datetime.datetime.now(),
                                                                                              new_call.get_entry_time())).total_seconds()
            if tle > 240:
                logger.critical("Time limit exceeded by {} secs".format(tle))
            else:
                if new_call.order_price != -1:
                    # placing oder
                    place_bo_order(new_call.get_call_dict())
                    logger.critical(new_call.get_call_dict())

            prev_list = copy.deepcopy(curr_list)

        if datetime.datetime.now().time() > square_off_time:
            logger.critical('Refresh Count is : {}'.format(refresh_count))
            logger.critical('Exit and Out')
            break


def init():
    global procap
    procap = website()
    procap.login()
    generateMISMultiplierDict.generate_mis_multiplier_dict()
    global kite
    kite = KiteConnect(api_key=zerodha_api_key)
    get_access_token()
    kite.set_access_token(zerodha_access_token)


if __name__ == '__main__':
    init()
    start()
    procap.stop_browser()
    invalidate_access_token()
