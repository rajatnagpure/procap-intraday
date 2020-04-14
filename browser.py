from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import bs4
from constants import *


class website:
    def __init__(self):
        # creating and using virtual display
        self.display = Display(visible=DISPLAY_FORMATE, size=(1024, 768))
        self.display.start()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--enable-infobars")
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("--enable-extensions")
        # Pass the argument 1 to allow and 2 to block
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

    # browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    def login(self):
        self.browser.get(LoginURL)
        self.wait = WebDriverWait(self.browser, 100)
        try:
            username_box = self.wait.until(
                lambda driver: self.browser.find_element_by_xpath(UsernameXpath))
            password_box = self.wait.until(
                lambda driver: self.browser.find_element_by_xpath(PasswordXpath))
            login_button = self.wait.until(
                lambda driver: self.browser.find_element_by_xpath(LoginButtonXpath))

            username_box.clear()
            password_box.clear()
            username_box.send_keys(Username)
            password_box.send_keys(Password)
            login_button.click()
            logger.info('Login Successful')

        except Exception as e:
            logger.error('failed to login {}'.format(str(e)))
        # self.allow_notification()
        self.browser.get(IntradayURL)

    # def allow_notification(self):
    #     try:
    #         notification = WebDriverWait(self.browser, 10).until(
    #             lambda driver: self.browser.find_element_by_xpath(NotificationProposeXpath))
    #         notification.click()
    #         print("Notification proposal accepted")
    #     except Exception as e:
    #         print('failed to Allow notification {}'.format(str(e)))

    def get_call(self):
        self.browser.refresh()
        self.wait.until(lambda driver: self.browser.find_element_by_xpath(CallTableRow))
        soup = bs4.BeautifulSoup(self.browser.page_source, 'lxml')
        table = soup.table
        table_rows = table.find_all('tr')
        tr = table_rows[2]
        td = tr.find_all('td')
        row = [i.text for i in td]
        return row

    def stop_browser(self):
        self.browser.quit()
        self.display.stop()
