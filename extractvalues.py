# from nsetools import Nse
from constants import *
from datetime import datetime


def get_all_matches(input_list, subs):
    res = []
    for i in input_list:
        if subs in i:
            res.append(i)
    return res


class extractValues:
    def __init__(self, row_call_detail):
        self.detail = row_call_detail[2]  # 'sell infy @637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        # Getting company name
        company_name_init_index = self.detail.find(' ') + 1
        company_name_last_index = self.detail.find('@') - 1
        self.company_name = self.detail[company_name_init_index:company_name_last_index]
        # Modify detail string. New string - '637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[company_name_last_index + 2:]
        # Getting Order price
        order_price_last_index = self.detail.find(',')
        try:
            self.order_price = float(self.detail[0:order_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting order price " + e.__str__())
            self.order_price = -1
        # Modify detail string. New String - 'sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[order_price_last_index + 1:]
        # Getting stop loss price.
        stop_loss_price_init_index = self.detail.find('@')
        stop_loss_price_last_index = self.detail.find(',')
        try:
            self.stop_loss_price = float(self.detail[stop_loss_price_init_index + 1:stop_loss_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting stop loss calculating our own " + e.__str__())
            if row_call_detail[1] == 'SELL':
                self.stop_loss_price = self.order_price + 2
            else:
                self.stop_loss_price = self.order_price - 2

        # Modify details string. New String- 'tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[stop_loss_price_last_index + 1:]
        if self.detail.find('exit') == -1:
            target_price_init_index = self.detail.find('@')
            target_price_last_index = self.detail.find('\n')
            try:
                self.target_price = float(self.detail[target_price_init_index + 1:target_price_last_index])
            except ValueError as e:
                logger.critical("Problem extracting target price calculating our own " + e.__str__())
                if row_call_detail[1] == 'SELL':
                    self.target_price = self.order_price - 3
                else:
                    self.target_price = self.order_price + 3
            self.detail = self.detail[target_price_last_index + 1:]
            self.exit_price = -1.0
        else:
            target_price_init_index = self.detail.find('@')
            target_price_decimal = self.detail.find('.')
            next_dot_index = self.detail[target_price_decimal + 1:].find('.') + target_price_decimal + 1
            if target_price_decimal + 1 == next_dot_index:
                try:
                    self.target_price = float(self.detail[target_price_init_index + 1:target_price_decimal])
                except ValueError as e:
                    logger.critical("Problem extracting target price calculating our own " + e.__str__())
                    if row_call_detail[1] == 'SELL':
                        self.target_price = self.target_price - 3
                    else:
                        self.target_price = self.target_price + 3
            else:
                try:
                    self.target_price = float(self.detail[target_price_init_index + 1:next_dot_index])
                except ValueError as e:
                    logger.critical("Problem extracting target price calculating our own " + e.__str__())
                    if row_call_detail[1] == 'SELL':
                        self.target_price = self.target_price - 3
                    else:
                        self.target_price = self.target_price + 3
            self.detail = self.detail[next_dot_index:]
            exit_price_init_index = self.detail.find('@')
            exit_price_last_index = self.detail.find('\n')
            try:
                self.exit_price = float(self.detail[exit_price_init_index + 1:exit_price_last_index])
            except ValueError as e:
                logger.critical("Problem extracting Exit value " + e.__str__())
                self.exit_price = -1
            self.detail = self.detail[exit_price_last_index + 1:]
        # ---------------------------------------------------------------------------------------------------------- #
        # Entry time detail
        entry_time_init_index = self.detail.find(':') + 2
        entry_time_last_index = self.detail.find('\n')
        entry_time_str = self.detail[entry_time_init_index:entry_time_last_index]
        str_format = '%I:%M %p'
        self.entry_time = datetime.strptime(entry_time_str, str_format).time()
        # ---------------------------------------------------------------------------------------------------------- #
        # some other detail
        self.call_action = row_call_detail[1]
        # ---------------------------------------------------------------------------------------------------------- #
        # getting stock Symbol or Ticker out of company name
        # it might be wrong and will return None if went wrong
        # it uses function get_all_matches
        close_matches = get_all_matches(all_company_quotes, self.company_name.lower().replace(" ", ""))
        close_match_fin = []
        for i in close_matches:
            number = all_company_quotes.index(i)
            if number % 2 != 0:
                number = number - 1
            close_match_fin.append(all_company_quotes[number])
        self.close_match_list = [i.upper() for i in close_match_fin]
        # self.mini = 100
        # self.my_stock = close_match_fin[0]
        # try:
        #     nse = Nse()
        #     for i in close_match_fin:
        #         q = abs(nse.get_quote(i)['lastPrice'] - self.order_price)
        #         if q < self.mini:
        #             self.mini = q
        #             self.my_stock = i
        # except Exception as e:
        #     logger.error('Exception Message'+e.__str__())

    def reuse(self, row_call_detail):
        self.detail = row_call_detail[2]  # 'sell infy @637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        # Getting company name
        company_name_init_index = self.detail.find(' ') + 1
        company_name_last_index = self.detail.find('@') - 1
        self.company_name = self.detail[company_name_init_index:company_name_last_index]
        # Modify detail string. New string - '637, sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[company_name_last_index + 2:]
        # Getting Order price
        order_price_last_index = self.detail.find(',')
        try:
            self.order_price = float(self.detail[0:order_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting order price " + e.__str__())
            self.order_price = -1
        # Modify detail string. New String - 'sl @640.05, tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[order_price_last_index + 1:]

        # Getting stop loss price.
        stop_loss_price_init_index = self.detail.find('@')
        stop_loss_price_last_index = self.detail.find(',')
        try:
            self.stop_loss_price = float(self.detail[stop_loss_price_init_index + 1:stop_loss_price_last_index])
        except ValueError as e:
            logger.critical("Problem extracting stop loss calculating our own " + e.__str__())
            if row_call_detail[1] == 'SELL':
                self.stop_loss_price = self.order_price + 2
            else:
                self.stop_loss_price = self.order_price - 2

        # Modify details string. New String- 'tgt @632.50\nTime Call Posted : 10:51
        # am\nTime Call hit : 11:31 am\n'
        self.detail = self.detail[stop_loss_price_last_index + 1:]
        if self.detail.find('exit') == -1:
            target_price_init_index = self.detail.find('@')
            target_price_last_index = self.detail.find('\n')
            try:
                self.target_price = float(self.detail[target_price_init_index + 1:target_price_last_index])
            except ValueError as e:
                logger.critical("Problem extracting target price calculating our own " + e.__str__())
                if row_call_detail[1] == 'SELL':
                    self.target_price = self.order_price - 3
                else:
                    self.target_price = self.order_price + 3
            self.detail = self.detail[target_price_last_index + 1:]
            self.exit_price = -1.0
        else:
            target_price_init_index = self.detail.find('@')
            target_price_decimal = self.detail.find('.')
            next_dot_index = self.detail[target_price_decimal + 1:].find('.') + target_price_decimal + 1
            if target_price_decimal + 1 == next_dot_index:
                try:
                    self.target_price = float(self.detail[target_price_init_index + 1:target_price_decimal])
                except ValueError as e:
                    logger.critical("Problem extracting target price calculating our own " + e.__str__())
                    if row_call_detail[1] == 'SELL':
                        self.target_price = self.target_price - 3
                    else:
                        self.target_price = self.target_price + 3
            else:
                try:
                    self.target_price = float(self.detail[target_price_init_index + 1:next_dot_index])
                except ValueError as e:
                    logger.critical("Problem extracting target price calculating our own " + e.__str__())
                    if row_call_detail[1] == 'SELL':
                        self.target_price = self.target_price - 3
                    else:
                        self.target_price = self.target_price + 3
            self.detail = self.detail[next_dot_index:]
            exit_price_init_index = self.detail.find('@')
            exit_price_last_index = self.detail.find('\n')
            try:
                self.exit_price = float(self.detail[exit_price_init_index + 1:exit_price_last_index])
            except ValueError as e:
                logger.critical("Problem extracting Exit value " + e.__str__())
                self.exit_price = -1
            self.detail = self.detail[exit_price_last_index + 1:]
        # ---------------------------------------------------------------------------------------------------------- #
        # Entry time detail
        entry_time_init_index = self.detail.find(':') + 2
        entry_time_last_index = self.detail.find('\n')
        entry_time_str = self.detail[entry_time_init_index:entry_time_last_index]
        str_format = '%I:%M %p'
        self.entry_time = datetime.strptime(entry_time_str, str_format).time()
        # ---------------------------------------------------------------------------------------------------------- #
        # some other detail
        self.call_action = row_call_detail[1]
        # ---------------------------------------------------------------------------------------------------------- #
        # getting stock Symbol or Ticker out of company name
        # it might be wrong and will return None if went wrong
        # it uses function get_all_matches
        close_matches = get_all_matches(all_company_quotes, self.company_name.lower().replace(" ", ""))
        close_match_fin = []
        for i in close_matches:
            number = all_company_quotes.index(i)
            if number % 2 != 0:
                number = number - 1
            close_match_fin.append(all_company_quotes[number])
        self.close_match_list = [i.upper() for i in close_match_fin]
        # self.mini = 100
        # self.my_stock = close_match_fin[0]
        # try:
        #     nse = Nse()
        #     for i in close_match_fin:
        #         q = abs(nse.get_quote(i)['lastPrice'] - self.order_price)
        #         if q < self.mini:
        #             self.mini = q
        #             self.my_stock = i
        # except Exception as e:
        #     logger.error('Exception Message'+e.__str__())

    def get_call_action(self):
        return self.call_action

    def get_company_name(self):
        return self.company_name

    def get_close_company_quote_list(self):
        return self.close_match_list

    def get_order_price(self):
        return self.order_price

    def get_stop_loss_price(self):
        return self.stop_loss_price

    def get_target_price(self):
        return self.target_price

    def get_exit_price(self):
        return self.exit_price

    def get_entry_time(self):
        return self.entry_time

    def get_call_dict(self):
        return {"action": self.call_action, "company_raw_text": self.company_name,
                "close_match_list": self.close_match_list, "order_price": self.order_price,
                "target_price": self.target_price, "stop_loss_price": self.stop_loss_price,
                "exit_price": self.exit_price, "entry_time": self.entry_time}
