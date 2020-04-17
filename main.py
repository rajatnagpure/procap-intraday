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
        logger.error("error while opening website and login : "+e.__str__())
        start()
        return

    # list and calls
    curr_list = procap.get_call()
    prev_list = copy.deepcopy(curr_list)
    new_call = extractValues(curr_list)
    refresh_count = 0

    while datetime.now().time() < market_opening_time:
        time.sleep(1)
    print('started')
    while 1:
        time.sleep(2)
        # refresh list
        try :
            curr_list = procap.get_call()
        except Exception as e:
            logger.error("Exception while refreshing call : " + e.__str__())

        refresh_count = refresh_count + 1
        if curr_list == prev_list:
            logger.info('getting pass')
            pass
        else:
            new_call.reuse(curr_list)
            if curr_list[2].find('exit') is -1:
                if (new_call.entry_time - datetime.now().time()).total_seconds() > 5*60:
                    pass
                else:
                    logger.info('Placing New order')
                    # Place new order
                    logger.info('Action ' + new_call.get_call_action())
                    logger.info('Company Name' + new_call.get_company_name())
                    # logger.info(call.get_company_quote())
                    logger.info('Order Price ' + new_call.get_order_price())
                    logger.info('Stop loss ' + new_call.get_stop_loss_price())
                    logger.info('Target ' + new_call.get_target_price())
                    logger.info('Exit ' + new_call.get_exit_price())
                    # wait for the trade to exit
                    time.sleep(15 * 60)
            else:
                logger.info('Exiting previously placed order')
            prev_list = copy.deepcopy(curr_list)

        if datetime.now().time() > square_off_time:
            # Place Square Off orders
            logger.info('placing square off orders')
            time.sleep(10)
            logger.info('Refresh Count is : {}'.format(refresh_count))
            logger.info('Exit and Out')
            procap.stop_browser()
            break


if __name__ == '__main__':
    start()
