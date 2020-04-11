from browser import website
from constants import *
from extractvalues import *

if __name__ == '__main__':
    procap = website()
    procap.login()
    call = extractValues(procap.get_call())
    print(call.get_call_action())
    print(call.get_company_name())
    print(call.get_company_quote())
    print(call.get_order_price())
    print(call.get_stop_loss_price())
    print(call.get_target_price())
    print(call.get_exit_price())
    call.reuse(procap.get_call())
    print(call.get_call_action())
    print(call.get_company_name())
    print(call.get_company_quote())
    print(call.get_order_price())
    print(call.get_stop_loss_price())
    print(call.get_target_price())
    print(call.get_exit_price())
    procap.stop_browser()
