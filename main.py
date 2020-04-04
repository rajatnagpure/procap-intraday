from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
import time
import os

display = Display(visible=0,size=(1024, 768))
display.start()

LoginURL = "https://procapital.mohdfaiz.com/login.php"
IntrdayURL = "https://procapital.mohdfaiz.com/intraday-calls.php"
UsernameXpath = """//*[@id="panel_dn"]/div[2]/form/div[1]/div/input"""
PasswordXpath = """//*[@id="panel_dn"]/div[2]/form/div[2]/div/input"""
LoginButtonXpath = """//*[@id="panel_dn"]/div[2]/form/div[3]/div/input"""
NotificationProposeXpath = """//*[@id="onesignal-popover-allow-button"]"""
Username = "rajatnagpure.rn@gmail.com"
Password = "Rajat@321"

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--enable-infobars")
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--enable-extensions")
# Pass the argument 1 to allow and 2 to block
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 1
})
#browser = webdriver.Chrome(chrome_options=chrome_options)
browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

browser.get(LoginURL)
# Now you can start using Selenium

#Logining in to the website
def login():
    try:
        username_box = WebDriverWait(browser, 10).until(lambda driver: browser.find_element_by_xpath(UsernameXpath))
        password_box = WebDriverWait(browser, 10).until(lambda driver: browser.find_element_by_xpath(PasswordXpath))
        login_button = WebDriverWait(browser, 10).until(lambda driver: browser.find_element_by_xpath(LoginButtonXpath))

        username_box.clear()
        password_box.clear()
        username_box.send_keys(Username)
        password_box.send_keys(Password)
        login_button.click()
        print('Login Successful')

    except Exception as e:
        print('failed to login {}'.format(str(e)))

def allow_notification():
    try:
        Allow_notification = WebDriverWait(browser, 10).until(
            lambda driver: browser.find_element_by_xpath(NotificationProposeXpath))
        Allow_notification.click()
        print("Notification proposal accepted")
    except Exception as e:
        print('failed to Allow notification {}'.format(str(e)))

if __name__ == '__main__':
    login()
    time.sleep(10)
    allow_notification()
    display.stop()