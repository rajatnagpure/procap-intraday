from constants import *
from datetime import datetime
import difflib


def get_all_matches(input_list, subs):
    res = []
    for i in input_list:
        if subs in i:
            res.append(i)
    return res + difflib.get_close_matches(subs, input_list)


def extract_values(row_call_detail):
    target_price = -1
    detail = row_call_detail[2]  # 'sell infy @637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
    # am\nTime Call hit : 11:31 am\n'
    # Getting company name
    company_name_init_index = detail.find(' ') + 1
    company_name_last_index = detail.find('@') - 1
    company_name = detail[company_name_init_index:company_name_last_index]
    # Modify detail string. New string - '637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
    # am\nTime Call hit : 11:31 am\n'
    detail = detail[company_name_last_index + 2:]
    # Getting Order price
    order_price_last_index = detail.find(',')
    try:
        order_price = float(detail[0:order_price_last_index])
    except ValueError as e:
        logger.critical("Problem extracting order price " + e.__str__())
        order_price = -1
    # Modify detail string. New String - 'sl @640.05, tgt @632.50\nTime Call Posted : 10:51
    # am\nTime Call hit : 11:31 am\n'
    detail = detail[order_price_last_index + 1:]
    # Getting stop loss price.
    stop_loss_price_init_index = detail.find('@')
    stop_loss_price_last_index = detail.find(',')
    try:
        stop_loss_price = float(detail[stop_loss_price_init_index + 1:stop_loss_price_last_index])
    except ValueError as e:
        logger.critical("Problem extracting stop loss calculating our own " + e.__str__())
        if row_call_detail[1] == 'SELL':
            stop_loss_price = order_price + 2
        else:
            stop_loss_price = order_price - 2

    # Modify details string. New String- 'tgt @632.50\nTime Call Posted : 10:51
    # am\nTime Call hit : 11:31 am\n'
    detail = detail[stop_loss_price_last_index + 1:]
    if detail.find('exit') == -1:
        target_price_init_index = detail.find('@')
        target_price_last_index = detail.find('\n')
        try:
            target_price = float(detail[target_price_init_index + 1:target_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting target price calculating our own " + e.__str__())
            if row_call_detail[1] == 'SELL':
                target_price = order_price - 3
            else:
                target_price = order_price + 3
        detail = detail[target_price_last_index + 1:]
        exit_price = -1.0
    else:
        target_price_init_index = detail.find('@')
        target_price_decimal = detail.find('.')
        next_dot_index = detail[target_price_decimal + 1:].find('.') + target_price_decimal + 1
        if target_price_decimal + 1 == next_dot_index:
            try:
                target_price = float(detail[target_price_init_index + 1:target_price_decimal])
            except ValueError as e:
                logger.critical("Problem extracting target price calculating our own " + e.__str__())
                if row_call_detail[1] == 'SELL':
                    target_price = target_price - 3
                else:
                    target_price = target_price + 3
        else:
            try:
                target_price = float(detail[target_price_init_index + 1:next_dot_index])
            except ValueError as e:
                logger.critical("Problem extracting target price calculating our own " + e.__str__())
                if row_call_detail[1] == 'SELL':
                    target_price = target_price - 3
                else:
                    target_price = target_price + 3
        detail = detail[next_dot_index:]
        exit_price_init_index = detail.find('@')
        exit_price_last_index = detail.find('\n')
        try:
            exit_price = float(detail[exit_price_init_index + 1:exit_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting Exit value " + e.__str__())
            exit_price = -1
        detail = detail[exit_price_last_index + 1:]
    # ---------------------------------------------------------------------------------------------------------- #
    # Entry time detail
    entry_time_init_index = detail.find(':') + 2
    entry_time_last_index = detail.find('\n')
    entry_time_str = detail[entry_time_init_index:entry_time_last_index]
    str_format = '%I:%M %p'
    entry_time = datetime.strptime(entry_time_str, str_format).time()
    # ---------------------------------------------------------------------------------------------------------- #
    # some other detail
    call_action = row_call_detail[1]
    # ---------------------------------------------------------------------------------------------------------- #
    # getting stock Symbol or Ticker out of company name
    # it might be wrong and will return None if went wrong
    # it uses function get_all_matches
    close_matches = get_all_matches(all_company_quotes, company_name.lower().replace(" ", ""))
    close_match_fin = set()
    for i in close_matches:
        number = all_company_quotes.index(i)
        if number % 2 != 0:
            number = number - 1
        close_match_fin.add(all_company_quotes[number])
    close_match_list = [i.upper() for i in close_match_fin]

    return {"action": call_action, "company_raw_text": company_name,
            "close_match_list": close_match_list, "order_price": order_price,
            "target_price": target_price, "stop_loss_price": stop_loss_price,
            "exit_price": exit_price, "entry_time": entry_time}
