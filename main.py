from browser import website
from constants import *
from extractvalues import *
from datetime import datetime
import time
import copy


def start():
    procap = website()
    procap.login()

    # list and calls
    curr_list = procap.get_call()
    prev_list = copy.deepcopy(curr_list)
    curr_call = extractValues(curr_list)
    prev_call = extractValues(prev_list)
    refresh_count = 0

    while datetime.now().time() < market_opening_time:
        time.sleep(1)
    print('started')
    while 1:
        # refresh list
        curr_list = procap.get_call()
        curr_call.reuse(curr_list)

        refresh_count = refresh_count + 1
        if curr_list == prev_list:
            logger.info('getting pass')
            pass
        else:
            if curr_call.get_exit_price() is -1.0:
                logger.info('Placing New order')
                # Place new order
                logger.info('Action ' + curr_call.get_call_action())
                logger.info('Company Name' + curr_call.get_company_name())
                # logger.info(call.get_company_quote())
                logger.info('Order Price ' + curr_call.get_order_price())
                logger.info('Stoploss ' + curr_call.get_stop_loss_price())
                logger.info('Target ' + curr_call.get_target_price())
                logger.info('Exit ' + curr_call.get_exit_price())
                time.sleep(15 * 60)
            else:
                logger.info('Exiting previous placed order')
            prev_list = curr_list
            prev_call = prev_call.reuse(prev_list)

        if datetime.now().time() > square_off_time:
            # Place Sqaure Off orders
            logger.info('placing square off orders')
            time.sleep(10)
            logger.info('Refresh Count is : {}'.format(refresh_count))
            logger.info('Exit and Out')
            procap.stop_browser()
            break


if __name__ == '__main__':
    start()
