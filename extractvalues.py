class extractValues:
    def __init__(self, row_call_detail):
        self.detail = row_call_detail[2]
        company_name_init_index = self.detail.find(' ') + 1
        company_name_last_index = self.detail.find('@') - 1
        self.company_name = self.detail[company_name_init_index:company_name_last_index]
        self.detail = self.detail[company_name_last_index + 2:]
        order_price_last_index = self.detail.find(',')
        self.order_price = float(self.detail[0:order_price_last_index])
        self.detail = self.detail[order_price_last_index + 1:]
        stop_loss_price_init_index = self.detail.find('@')
        stop_loss_price_last_index = self.detail.find(',')
        self.stop_loss_price = float(self.detail[stop_loss_price_init_index + 1:stop_loss_price_last_index])
        self.detail = self.detail[stop_loss_price_last_index + 1:]
        if self.detail.find('exit') == -1:
            target_price_init_index = self.detail.find('@')
            target_price_last_index = self.detail.find('\n')
            self.target_price = float(self.detail[target_price_init_index + 1:target_price_last_index])
            self.detail = self.detail[target_price_last_index + 1:]
            self.exit_price = -1.0
        else:
            target_price_init_index = self.detail.find('@')
            target_price_decimal = self.detail.find('.')
            next_dot_index = self.detail[target_price_decimal + 1:].find('.') + target_price_decimal + 1
            if target_price_decimal + 1 == next_dot_index:
                self.target_price = float(self.detail[target_price_init_index + 1:target_price_decimal])
            else:
                self.target_price = float(self.detail[target_price_init_index + 1:next_dot_index])
            self.detail = self.detail[next_dot_index:]
            exit_price_init_index = self.detail.find('@')
            exit_price_last_index = self.detail.find('\n')
            self.exit_price = float(self.detail[exit_price_init_index + 1:exit_price_last_index])
        # some other detail
        self.call_action = row_call_detail[1]

    def reuse(self, row_call_detail):
        self.detail = row_call_detail[2]
        company_name_init_index = self.detail.find(' ') + 1
        company_name_last_index = self.detail.find('@') - 1
        self.company_name = self.detail[company_name_init_index:company_name_last_index]
        self.detail = self.detail[company_name_last_index + 2:]
        order_price_last_index = self.detail.find(',')
        self.order_price = float(self.detail[0:order_price_last_index])
        self.detail = self.detail[order_price_last_index + 1:]
        stop_loss_price_init_index = self.detail.find('@')
        stop_loss_price_last_index = self.detail.find(',')
        self.stop_loss_price = float(self.detail[stop_loss_price_init_index + 1:stop_loss_price_last_index])
        self.detail = self.detail[stop_loss_price_last_index + 1:]
        if self.detail.find('exit') == -1:
            target_price_init_index = self.detail.find('@')
            target_price_last_index = self.detail.find('\n')
            self.target_price = float(self.detail[target_price_init_index + 1:target_price_last_index])
            self.detail = self.detail[target_price_last_index + 1:]
            self.exit_price = -1.0
        else:
            target_price_init_index = self.detail.find('@')
            target_price_decimal = self.detail.find('.')
            next_dot_index = self.detail[target_price_decimal + 1:].find('.') + target_price_decimal + 1
            if target_price_decimal + 1 == next_dot_index:
                self.target_price = float(self.detail[target_price_init_index + 1:target_price_decimal])
            else:
                self.target_price = float(self.detail[target_price_init_index + 1:next_dot_index])
            self.detail = self.detail[next_dot_index:]
            exit_price_init_index = self.detail.find('@')
            exit_price_last_index = self.detail.find('\n')
            self.exit_price = float(self.detail[exit_price_init_index + 1:exit_price_last_index])
        # some other detail
        self.call_action = row_call_detail[1]

    def get_call_action(self):
        return self.call_action

    def get_company_name(self):
        return self.company_name

    def get_order_price(self):
        return self.order_price

    def get_stop_loss_price(self):
        return self.stop_loss_price

    def get_target_price(self):
        return self.target_price

    def get_exit_price(self):
        return self.exit_price
