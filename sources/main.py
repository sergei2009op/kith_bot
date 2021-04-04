import os, sys, zipfile, csv, time, random
import proxy
from select_path import select_paths
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
autofill_data = []


def read_tasks():
    with open(resource_path('tasks.csv'), 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for task in reader:
            tasks.append(task)


def read_autofill_data(user_num):
    with open(resource_path('autofill.csv'), 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')
        for i, row in enumerate(reader):
            if i == user_num-1:
                autofill_data.append(row)


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

        read_autofill_data(task_num)

        choose_size(driver)
        add_to_cart(driver)
        open_cart(driver)
        wait_for_the_end_of_queue(driver)
        autofill(driver, task_num)


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

    driver_path = resource_path('chromedriver')
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
        find_element(driver, select_paths['email']).send_keys(tasks[task_num]['email'])
        find_element(driver, select_paths['password']).send_keys(tasks[task_num]['password'])
        find_element(driver, select_paths['login_button']).click()
    except:
        print('Logged in')


def open_product_page(driver):
    driver.get(product_url)


def wait_for_product(driver):
    try:
        wait = WebDriverWait(driver, 0.6)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, select_paths['sizes_box'])))
    except:
        driver.refresh()
        wait_for_product(driver)


def get_sizes(driver):
    combobox = find_element(driver, select_paths['sizes_box'])
    select = Select(combobox)
    sizes.clear()
    for option in select.options:
        size = option.get_attribute('value')
        sizes.append(size)


def choose_size(driver):
    value = random.choice(sizes)
    try:
        select_from_combobox(driver, select_paths['sizes_box'], value)
    except:
        print(f'Size {value} not found')
        sizes.remove(value)
        choose_size(driver)


def select_from_combobox(driver, combobox_selector, value):
    combobox = find_element(driver, combobox_selector)
    Select(combobox).select_by_value(value)


def add_to_cart(driver):
    find_element(driver, select_paths['add_to_cart_button']).click()


def open_cart(driver):
    cart_url = 'https://eu.kith.com/pages/international-checkout#Global-e_International_Checkout'
    driver.get(cart_url)


def wait_for_the_end_of_queue(driver):
    wait = WebDriverWait(driver, 300)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, select_paths['address_frame'])))
    while True:
        try:
            find_element(driver, select_paths['add_alt_address']).click()
            break
        except:
            print('Waiting...')

        time.sleep(0.1)


# noinspection PyTypeChecker
def autofill(driver, task_num):
    fill_form(find_element(driver, select_paths['first_name']), autofill_data[task_num-1]['first_name'])
    fill_form(find_element(driver, select_paths['last_name']), autofill_data[task_num-1]['last_name'])
    fill_form(find_element(driver, select_paths['email_cart']), autofill_data[task_num-1]['email_cart'])
    select_from_combobox(driver, select_paths['country_box'], autofill_data[task_num-1]['country_box'])
    fill_form(find_element(driver, select_paths['address_line1']), autofill_data[task_num-1]['address_line1'])
    fill_form(find_element(driver, select_paths['address_line2']), autofill_data[task_num-1]['address_line2'])
    fill_form(find_element(driver, select_paths['city']), autofill_data[task_num-1]['city'])
    fill_form(find_element(driver, select_paths['postcode']), autofill_data[task_num-1]['postcode'])
    fill_form(find_element(driver, select_paths['mobile']), autofill_data[task_num-1]['mobile'])

    fill_form(find_element(driver, select_paths['alt_first_name']), autofill_data[task_num-1]['alt_first_name'])
    fill_form(find_element(driver, select_paths['alt_last_name']), autofill_data[task_num-1]['alt_last_name'])
    select_from_combobox(driver, select_paths['alt_country_box'], autofill_data[task_num-1]['alt_country_box'])
    find_element(driver, select_paths['alt_address_line1']).send_keys(autofill_data[task_num-1]['alt_address_line1'])
    find_element(driver, select_paths['alt_address_line2']).send_keys(autofill_data[task_num-1]['alt_address_line2'])
    find_element(driver, select_paths['alt_city']).send_keys(autofill_data[task_num-1]['alt_city'])
    find_element(driver, select_paths['alt_postcode']).send_keys(autofill_data[task_num-1]['alt_postcode'])
    find_element(driver, select_paths['alt_mobile']).send_keys(autofill_data[task_num-1]['alt_mobile'])

    payment_frame = find_element(driver, select_paths['payment_frame'])
    driver.switch_to.frame(payment_frame)

    find_element(driver, select_paths['card_number']).send_keys(autofill_data[task_num-1]['card_number'])
    find_element(driver, select_paths['exp_month']).send_keys(autofill_data[task_num-1]['exp_month'])
    find_element(driver, select_paths['exp_year']).send_keys(autofill_data[task_num-1]['exp_year'])
    find_element(driver, select_paths['cvv']).send_keys(autofill_data[task_num-1]['cvv'])

    # find_element(driver, select_paths['order_button']).click()


read_tasks()

Parallel(n_jobs=-1)(delayed(run_task)(i) for i in range(1, 3))
