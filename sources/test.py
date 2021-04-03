import os, sys, zipfile, csv, time
import random
import proxy
from selectors import xpaths
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


product_url = 'https://eu.kith.com/collections/mens-footwear-sneakers/products/cn165627c'
sizes = ['5', '6', '10', '11', '11.5']
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


def run_task(task_num):
    driver = get_chromedriver(task_num, use_proxy=True)
    # open_login_page(driver)
    # autologin(task_num, driver)
    # open_product_page(driver)
    # add_to_cart(driver)
    open_cart(driver)
    autofill(driver)


def fill_form_with_chars(form, string):
    form.click()
    form.clear()
    form.send_keys(string)


def open_login_page(driver):
    login_url = 'https://eu.kith.com/account'
    driver.get(login_url)
    time.sleep(1)
    driver.get(login_url)


def autologin(task_num, driver):
    try:
        email = driver.find_element_by_id('CustomerEmail')
        password = driver.find_element_by_id('CustomerPassword')

        fill_form_with_chars(email, tasks[task_num]['email'])
        fill_form_with_chars(password, tasks[task_num]['password'])

        button = driver.find_element_by_xpath(xpaths['login_button'])
        button.click()
    except:
        print('Logged in')


def open_product_page(driver):
    driver.get(product_url)
    choose_size(driver)


def choose_size(driver):
    is_size_found = False
    while not is_size_found:
        value = random.choice(sizes)
        try:
            select_from_combobox(driver, xpaths['sizes_box'], value)
            is_size_found = True
        except:
            sizes.remove(value)
            print('Size not found')


def select_from_combobox(driver, combobox, value):
    Select(driver.find_element_by_xpath(combobox)).select_by_value(value)


def add_to_cart(driver):
    button = driver.find_element_by_xpath(xpaths['add_to_cart'])
    button.click()


def open_cart(driver):
    cart_url = 'https://eu.kith.com/pages/international-checkout#Global-e_International_Checkout'
    driver.get(cart_url)


def autofill(driver):
    WebDriverWait(driver, 180).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpaths['address_frame'])))

    while True:
        try:
            driver.find_element_by_xpath(xpaths['first_name']).send_keys('Pipi')
            break
        except:
            print('Waiting...')

        time.sleep(0.5)

    driver.find_element_by_xpath(xpaths['last_name']).send_keys('Pupu')
    driver.find_element_by_xpath(xpaths['email_cart']).send_keys('poopy@pip.com')
    select_from_combobox(driver, xpaths['country_box'], '159')
    driver.find_element_by_xpath(xpaths['address_line1']).send_keys('Red Square')
    driver.find_element_by_xpath(xpaths['address_line2']).send_keys('Saint Basil\'s Cathedral')
    driver.find_element_by_xpath(xpaths['city']).send_keys('Moscow')
    driver.find_element_by_xpath(xpaths['postcode']).send_keys('123123')
    driver.find_element_by_xpath(xpaths['mobile']).send_keys('88005553535')
    driver.find_element_by_xpath(xpaths['add_alt_address']).click()
    driver.find_element_by_xpath(xpaths['alt_first_name']).send_keys('Pipi')
    driver.find_element_by_xpath(xpaths['alt_last_name']).send_keys('Pupu')
    select_from_combobox(driver, xpaths['alt_country_box'], '159')
    driver.find_element_by_xpath(xpaths['alt_address_line1']).send_keys('Red Square')
    driver.find_element_by_xpath(xpaths['alt_address_line2']).send_keys('Saint Basil\'s Cathedral')
    driver.find_element_by_xpath(xpaths['alt_city']).send_keys('Moscow')
    driver.find_element_by_xpath(xpaths['alt_postcode']).send_keys('123123')
    driver.find_element_by_xpath(xpaths['alt_mobile']).send_keys('88005553535')

    WebDriverWait(driver, 180).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpaths['payment_frame'])))

    driver.find_element_by_xpath(xpaths['card_number']).send_keys('4276434365658787')
    driver.find_element_by_xpath(xpaths['exp_month']).send_keys('11')
    driver.find_element_by_xpath(xpaths['exp_year']).send_keys('22')
    driver.find_element_by_xpath(xpaths['cvv']).send_keys('621')
    # driver.find_element_by_xpath(xpaths['order_button']).click()


Parallel(n_jobs=-1)(delayed(run_task)(i) for i in range(1, 2))
