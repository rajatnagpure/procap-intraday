from extractvalues import *
from datetime import datetime
from time import sleep
import copy
from procapital import *
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
    at_dict = {"access_token": zerodha_access_token, "time": datetime.now().strftime("%m/%d/%Y")}
    try:
        with open('access_token.json', 'w') as json_file:
            json.dump(at_dict, json_file)
    except Exception as e:
        logger.critical("Problem dumping access Token into json file: {}".format(e))


def invalidate_access_token():
    kite.invalidate_access_token(zerodha_access_token)


def get_company_quote(close_match_list, order_price):
    if len(close_match_list) is 0:
        return "", 0

    my_stock = close_match_list[0]
    mini = 100
    try:
        temp_list = ["NSE:" + i for i in close_match_list]
        ltp_list = kite.ltp(temp_list)
    except Exception as e:
        logger.critical("Problem resolving company qoute: {}".format(e))
        return "", 0

    for i in close_match_list:
        if "NSE:" + i not in ltp_list.keys():
            continue
        diff = abs(ltp_list["NSE:" + i]["last_price"] - order_price)
        if diff < mini:
            mini = diff
            my_stock = i

    return my_stock, mini


def get_mis_buyable_quantity(stock_quote, order_price):
    # total_margin_available = kite.margins()["equity"]["net"]
    mis_multi = mis_multipliers[stock_quote]
    total_quantity = int((total_margin_available * mis_multi) / order_price)
    return total_quantity


def place_co_order(order_detail):
    action = order_detail["action"]
    order_price = order_detail["order_price"]
    stock_quote, mini = get_company_quote(order_detail["close_match_list"], order_price)
    if mini > 10 or stock_quote is "":
        return
    quantity = get_mis_buyable_quantity(stock_quote, order_price)
    mini = mini + process_calculation_margin
    if order_detail["target_price"] > order_detail["order_price"]:
        order_price = order_detail["order_price"] + mini
        target_price = order_detail["target_price"] + mini
        stop_loss_trigger = order_detail["stop_loss_price"] + mini
        action = 'BUY'
    else:
        order_price = order_detail["order_price"] - mini
        target_price = order_detail["target_price"] - mini
        stop_loss_trigger = order_detail["stop_loss_price"] - mini
        action = 'SELL'
    try:
        order_id = kite.place_order(kite.VARIETY_CO,
                                    kite.EXCHANGE_NSE,
                                    stock_quote,
                                    action,
                                    quantity,
                                    kite.PRODUCT_MIS,
                                    kite.ORDER_TYPE_LIMIT,
                                    price=order_price,
                                    trigger_price=stop_loss_trigger)
    except Exception as e:
        logger.critical("Problem Placing order: {}\n so quiting and proceeding".format(e))
        return
    try:
        logger.critical("Order placed: ltp is: {}".format(kite.ltp("NSE:" + stock_quote)))
    except Exception as e:
        logger.critical("Problem quoting the company ltp after placing order:{}".format(e))
    # now looping for exit check
    sleep(5 * 60)
    order_book = kite.orders()
    co_second_leg_order_id = 0
    for order in order_book:
        if order["parent_order_id"] == order_id:
            co_second_leg_order_id = order["order_id"]
            break
    # check if order succeeded
    print("Parent Order ID:. {}".format(order_id))
    print("Second leg Order ID:. {}".format(co_second_leg_order_id))
    logger.critical("Parent Order ID:. {}".format(order_id))
    logger.critical("Second leg Order ID:. {}".format(co_second_leg_order_id))
    if kite.order_history(order_id)[-1]["status"] != 'COMPLETE':
        try:
            kite.cancel_order('co', order_id=co_second_leg_order_id, parent_order_id=order_id)
        except Exception as e:
            logger.critical("Problem cancelling order: {}".format(e))
        return
    # check for success of order.
    logger.critical(get_specific_call(order_detail["company_raw_text"]))
    while 1:
        sleep(4)
        exit_call = get_specific_call(order_detail["company_raw_text"])
        exit_detail = extract_values(exit_call)
        if exit_call[3] == 'Call Closed':
            if exit_call[4] != 'Stop Loss\n':
                sleep(100)
                logger.critical("Exiting order on Call Achieved")
                try:
                    kite.exit_order('co', order_id=co_second_leg_order_id, parent_order_id=order_id)
                except Exception as e:
                    logger.critical("Problem exiting order: {}".format(e))
                return
            else:
                logger.critical("Exiting order on Stop Loss Hit")
                return
        if exit_detail["exit_price"] != -1.0:
            logger.critical("Exiting order on call modified exit price")
            try:
                kite.exit_order('co', order_id=co_second_leg_order_id, parent_order_id=order_id)
            except Exception as e:
                logger.critical("Problem exiting order: {}".format(e))
            return
        if datetime.now().time() > square_off_time:
            logger.critical("Exiting order on market close time")
            try:
                kite.exit_order('co', order_id=co_second_leg_order_id, parent_order_id=order_id)
            except Exception as e:
                logger.critical("Problem exiting order: {}".format(e))
            return
        logger.critical("getting pass in co order function")


# ---------------------------------------------------------------------------------------------------------------------------------- #
# -------------------------------------------------------ZERODHA UTILS ENDS--------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------------------------- #


def start():
    # list and calls
    curr_list = get_call()
    prev_list = copy.deepcopy(curr_list)
    new_call = extract_values(curr_list)
    logger.critical(new_call)

    refresh_count = 0
    print("about to start")
    while datetime.now().time() < market_opening_time:
        sleep(1)
    print('started')
    while 1:
        sleep(1)
        # refresh list
        try:
            curr_list = get_call()
        except Exception as e:
            logger.critical("problem Refreshing call: {}".format(e))

        refresh_count = refresh_count + 1
        if curr_list == prev_list:
            logger.critical('getting pass')
        else:
            try:
                new_call = extract_values(curr_list)
            except Exception as e:
                logger.critical("Exception while extracting call : " + e.__str__())
                prev_list = copy.deepcopy(curr_list)
                continue

            tle = (datetime.combine(datetime.now(), datetime.now().time()) - datetime.combine(datetime.now(),
                                                                                              new_call[
                                                                                                  "entry_time"])).total_seconds()
            if tle > 240:
                logger.critical("Time limit exceeded by {} secs".format(tle))
            else:
                if new_call["order_price"] != -1:
                    logger.critical("new order time: {}".format(tle))
                    logger.critical("Order Detail is : {}".format(new_call))
                    place_co_order(new_call)

            prev_list = copy.deepcopy(curr_list)

        if datetime.now().time() > square_off_time:
            logger.critical('Refresh Count is : {}'.format(refresh_count))
            logger.critical('Exit and Out')
            break


def init():
    generateMISMultiplierDict.generate_mis_multiplier_dict()
    global kite
    kite = KiteConnect(api_key=zerodha_api_key)
    get_access_token()
    kite.set_access_token(zerodha_access_token)


if __name__ == '__main__':
    init()
    start()
    invalidate_access_token()
