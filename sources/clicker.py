import time
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

xpaths = {'sizes': '/html/body/div[2]/main/div[2]/section/div[2]/form/div/div[2]/select',
          'add_to_cart': '/html/body/div[2]/main/div[2]/section/div[2]/form/button',
          'name': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[2]/div/input',
          'surname': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[3]/div/input',
          'email': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[4]/div/input',
          'country': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[5]/div/select',
          'address_line1': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[6]/div/input',
          'address_line2': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[7]/div/input',
          'city': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[8]/div/input',
          'postcode': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[10]/div/input',
          'mobile': '/html/body/div[2]/div[2]/form[1]/div[1]/div[1]/div/div[2]/div[12]/div/input',
          'add_alt_address': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[2]/div[6]/input',
          'alt_name': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[1]/div/input',
          'alt_surname': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[2]/div/input',
          'alt_country': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[3]/div/select',
          'alt_address_line1': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[4]/div/input',
          'alt_address_line2': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[5]/div/input',
          'alt_city': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[6]/div/input',
          'alt_postcode': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[8]/div/input',
          'alt_mobile': '/html/body/div[2]/div[2]/form[1]/div[1]/div[2]/div/div[2]/div[3]/div[10]/div/input',
          'card_number': '/html/body/form/div/div/div[1]/div/input',
          'exp_month': '/html/body/form/div/div/div[2]/div/div/div[1]/div/select',
          'exp_year': '/html/body/form/div/div/div[2]/div/div/div[2]/div/select',
          'cvv': '/html/body/form/div/div/div[3]/div/input'}


def select_size(size_pos=2):
    #  Первый (даже если единственный) размер при выборе имеет индекс 2
    Select(driver.find_element_by_xpath(xpaths.get('sizes'))).select_by_index(size_pos)


select_size()
