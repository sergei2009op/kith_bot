import os, sys, zipfile, csv, time
import proxy
from xpaths import xpaths
from selenium.webdriver import ChromeOptions, Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from joblib import Parallel, delayed


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


tasks = []
with open(resource_path('tasks.csv'), 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for task in reader:
        tasks.append(task)

window_size = '700,700'
driver_path = resource_path('chromedriver')


def create_proxy_ext(ext_dir):
    with zipfile.ZipFile(ext_dir, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js())


def get_chromedriver(task_num, use_proxy=False, user_agent=None):
    chrome_options = ChromeOptions()
    chrome_options.add_argument(f'window-size={window_size}')

    user_data_dir = f'Selenium_{task_num}'
    chrome_options.add_argument(f'user-data-dir={user_data_dir}')
    chrome_options.add_argument(f'profile-directory=Profile 1')
    chrome_options.add_experimental_option('detach', True)

    if use_proxy:
        ext_file = 'proxy_auth_ext.zip'
        ext_dir = user_data_dir + '/' + ext_file
        create_proxy_ext(ext_dir)
        chrome_options.add_extension(ext_dir)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def open_drivers(task_num):
    driver = get_chromedriver(task_num, use_proxy=True)
    product_url = 'https://eu.kith.com/collections/mens-footwear-sneakers/products/cn165627c'
    open_login_page(task_num, driver)
    open_product_page(product_url, driver)
    select_from_box(xpaths['sizes'], driver, '10.5')
    add_to_cart(driver)
    autofill_the_cart_eu(driver)


def fill_form_with_chars(form, string):
    form.click()
    form.clear()
    form.send_keys(string)


def open_login_page(task_num, driver):
    login_url = 'https://eu.kith.com/account'
    driver.get(login_url)

    try:
        email = driver.find_element_by_id('CustomerEmail')
        password = driver.find_element_by_id('CustomerPassword')

        fill_form_with_chars(email, tasks[task_num]['email'])
        fill_form_with_chars(password, tasks[task_num]['password'])

        button = driver.find_element_by_xpath(xpaths['login_button'])
        button.click()
    except:
        print('Logged in')


def open_product_page(product_url, driver):
    driver.get(product_url)


def select_from_box(box, driver, val='10.5'):
    Select(driver.find_element_by_xpath(box)).select_by_value(val)


def add_to_cart(driver):
    button = driver.find_element_by_xpath(xpaths['add_to_cart'])
    button.click()


def autofill_the_cart_eu(driver):
    cart_url = 'https://eu.kith.com/pages/international-checkout#Global-e_International_Checkout'
    driver.get(cart_url)
    time.sleep(15)
    fill_form_with_chars(driver.find_element_by_id("CheckoutData_BillingLastName"), 1)
    select_from_box(driver.find_element_by_id("BillingCountryID"), driver, 'Russia')


Parallel(n_jobs=-1)(delayed(open_drivers)(i) for i in range(1, 2))
