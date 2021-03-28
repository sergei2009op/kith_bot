import time
from xpaths import xpaths
from selenium import webdriver
from selenium.webdriver.support.ui import Select

options = webdriver.ChromeOptions()
#  options.add_argument("--incognito")
#  options.add_argument("--headless")
options.add_argument("user-data-dir=Selenium")
options.add_argument('profile-directory=Profile 2')

driver = webdriver.Chrome('../sources/chromedriver', options=options)
driver.get('https://yandex.ru/')
time.sleep(2)


def select_size(size_pos=2):
    #  Первый (даже если единственный) размер при выборе имеет индекс 2
    Select(driver.find_element_by_xpath(xpaths.get('sizes'))).select_by_index(size_pos)


select_size()
