from browser import website
from constants import *
from extractvalues import *
from datetime import datetime
import time
import copy


def start():
    try:
        procap = website()
        procap.login()
    except Exception as e:
        logger.error("error while opening website and login : " + e.__str__())
        start()
        return

    # list and calls
    curr_list = procap.get_call()
    prev_list = copy.deepcopy(curr_list)
    new_call = extractValues(curr_list)

    logger.critical('Action {}'.format(new_call.get_call_action()))
    logger.critical('Company Name{}'.format(new_call.get_company_name()))
    # logger.critical()(call.get_company_quote())
    logger.critical('Order Price {}'.format(new_call.get_order_price()))
    logger.critical('Stop loss {}'.format(new_call.get_stop_loss_price()))
    logger.critical('Target {}'.format(new_call.get_target_price()))
    logger.critical('Exit {}'.format(new_call.get_exit_price()))

    refresh_count = 0

    while datetime.now().time() < market_opening_time:
        time.sleep(1)
    print('started')
    while 1:
        time.sleep(2)
        # refresh list
        try:
            curr_list = procap.get_call()
        except Exception as e:
            logger.critical("Exception while refreshing call : " + e.__str__())
            procap.stop_browser()
            time.sleep(500)
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

            if curr_list[2].find('exit') is -1:
                if (datetime.combine(datetime.now(), datetime.now().time()) - datetime.combine(datetime.now(),
                                                                                               new_call.get_entry_time())).total_seconds() > 60:
                    logger.critical("Time limit exceeded")
                else:
                    if new_call.order_price != -1:
                        logger.critical('Placing New order')
                        # Place new order
                        logger.critical('Action {}'.format(new_call.get_call_action()))
                        logger.critical('Company Name{}'.format(new_call.get_company_name()))
                        # logger.critical()(call.get_company_quote())
                        logger.critical('Order Price {}'.format(new_call.get_order_price()))
                        logger.critical('Stop loss {}'.format(new_call.get_stop_loss_price()))
                        logger.critical('Target {}'.format(new_call.get_target_price()))
                        logger.critical('Exit {}'.format(new_call.get_exit_price()))
                        # wait for the trade to exit
                        time.sleep(5 * 60)
            else:
                logger.critical('Exiting previously placed order')
                if new_call.exit_price == -1:
                    # Exit on MARKET PRICE
                    pass
                else:
                    # Exit on LIMIT PRICE
                    pass
            prev_list = copy.deepcopy(curr_list)

        if datetime.now().time() > square_off_time:
            # Place Square Off orders
            logger.critical('placing square off orders')
            time.sleep(10)
            logger.critical('Refresh Count is : {}'.format(refresh_count))
            logger.critical('Exit and Out')
            procap.stop_browser()
            break


if __name__ == '__main__':
    start()
