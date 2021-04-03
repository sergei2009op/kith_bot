import os, sys, zipfile, csv, time, random
import proxy
from selectors import selectors
from selenium.webdriver import ChromeOptions, Chrome
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


is_first_run = False
is_any_size = False
product_url = 'https://eu.kith.com/products/cn165523c'
sizes = ['5', '6', '7', '10', '11', '11.5']
tasks = []


def read_tasks():
    with open(resource_path('tasks.csv'), 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for task in reader:
            tasks.append(task)


def run_task(task_num):
    if is_first_run:
        driver = get_chromedriver(task_num, True)
        open_login_page(driver)
        autologin(task_num, driver)
    else:
        driver = get_chromedriver(task_num, True)
        open_product_page(driver)
        wait_for_product(driver)

        if is_any_size:
            get_sizes(driver)

        choose_size(driver)
        add_to_cart(driver)
        open_cart(driver)
        wait_for_the_end_of_queue(driver)
        autofill(driver)


def get_chromedriver(task_num, use_proxy=False):
    chrome_options = ChromeOptions()
    window_size = '700,700'
    chrome_options.add_argument(f'window-size={window_size}')
    user_data_dir = f'Selenium_{task_num}'
    chrome_options.add_argument(f'user-data-dir={user_data_dir}')
    chrome_options.add_argument(f'profile-directory=Profile 1')
    chrome_options.add_experimental_option('detach', True)

    if use_proxy:
        ext_file = f'proxy_ext_{task_num}.zip'
        create_proxy_ext(ext_file)
        chrome_options.add_extension(ext_file)

    driver_path = resource_path('chromedriver_89')
    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def create_proxy_ext(ext_dir):
    with zipfile.ZipFile(ext_dir, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js())


def open_login_page(driver):
    login_url = 'https://eu.kith.com/account'
    driver.get(login_url)
    time.sleep(1)
    driver.get(login_url)


def find_element(driver, selector):
    element = driver.find_element_by_css_selector(selector)
    return element


def fill_form(form, string):
    form.clear()
    form.send_keys(string)


def autologin(task_num, driver):
    try:
        find_element(driver, selectors['email']).send_keys(tasks[task_num]['email'])
        find_element(driver, selectors['password']).send_keys(tasks[task_num]['password'])
        find_element(driver, selectors['login_button']).click()
    except:
        print('Logged in')


def open_product_page(driver):
    driver.get(product_url)


def wait_for_product(driver):
    try:
        wait = WebDriverWait(driver, 0.6)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['sizes_box'])))
    except:
        driver.refresh()
        wait_for_product(driver)


def get_sizes(driver):
    combobox = find_element(driver, selectors['sizes_box'])
    select = Select(combobox)
    sizes.clear()
    for option in select.options:
        size = option.get_attribute('value')
        sizes.append(size)


def choose_size(driver):
    value = random.choice(sizes)
    try:
        select_from_combobox(driver, selectors['sizes_box'], value)
    except:
        print(f'Size {value} not found')
        sizes.remove(value)
        choose_size(driver)


def select_from_combobox(driver, combobox_selector, value):
    combobox = find_element(driver, combobox_selector)
    Select(combobox).select_by_value(value)


def add_to_cart(driver):
    find_element(driver, selectors['add_to_cart_button']).click()


def open_cart(driver):
    cart_url = 'https://eu.kith.com/pages/international-checkout#Global-e_International_Checkout'
    driver.get(cart_url)


def wait_for_the_end_of_queue(driver):
    wait = WebDriverWait(driver, 300)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, selectors['address_frame'])))
    while True:
        try:
            find_element(driver, selectors['add_alt_address']).click()
            break
        except:
            print('Waiting...')

        time.sleep(0.1)


def autofill(driver):
    fill_form(find_element(driver, selectors['first_name']), 'Pipi')
    fill_form(find_element(driver, selectors['last_name']), 'Pupu')
    fill_form(find_element(driver, selectors['email_cart']), 'poopy@pip.com')
    select_from_combobox(driver, selectors['country_box'], '159')
    fill_form(find_element(driver, selectors['address_line1']), 'Red Square')
    fill_form(find_element(driver, selectors['address_line2']), 'Saint Basil\'s Cathedral')
    fill_form(find_element(driver, selectors['city']), 'Moscow')
    fill_form(find_element(driver, selectors['postcode']), '123123')
    fill_form(find_element(driver, selectors['mobile']), '88005553535')

    fill_form(find_element(driver, selectors['alt_first_name']), 'Pipi')
    fill_form(find_element(driver, selectors['alt_last_name']), 'Pupu')
    select_from_combobox(driver, selectors['alt_country_box'], '159')
    find_element(driver, selectors['alt_address_line1']).send_keys('Red Square')
    find_element(driver, selectors['alt_address_line2']).send_keys('Saint Basil\'s Cathedral')
    find_element(driver, selectors['alt_city']).send_keys('Moscow')
    find_element(driver, selectors['alt_postcode']).send_keys('123123')
    find_element(driver, selectors['alt_mobile']).send_keys('88005553535')

    payment_frame = find_element(driver, selectors['payment_frame'])
    driver.switch_to.frame(payment_frame)

    find_element(driver, selectors['card_number']).send_keys('4276434365658787')
    find_element(driver, selectors['exp_month']).send_keys('11')
    find_element(driver, selectors['exp_year']).send_keys('22')
    find_element(driver, selectors['cvv']).send_keys('621')

    # find_element(driver, selectors['order_button']).click()


read_tasks()
Parallel(n_jobs=-1)(delayed(run_task)(i) for i in range(1, 3))
