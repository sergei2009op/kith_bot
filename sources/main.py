import proxy
from paths import paths
import os, sys, subprocess, platform
import zipfile, csv, time, random
import requests
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from joblib import Parallel, delayed


is_login_needed = bool(int(input('Do you need to log in? [1 for yes / 0 for no]: ')))
if not is_login_needed:
    is_link_from_monitor = bool(int(input('Do you want to open product manually? [1 for yes / 0 for no]: ')))
    is_any_size = bool(int(input('Do you want to choose any available size? [1 for yes / 0 for no]: ')))
region = input('Enter region? ["eu" for eu / ENTER for us]: ')


product_url = 'https://kith.com/products/aagw0265'
sizes = ['5', '6', '7', '10', '11', '11.5']
tasks = []


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


def login():
    if os.path.exists(resource_path('settings.txt')):
        with open(resource_path('settings.txt'), 'r', encoding='utf-8') as f:
            content = f.readlines()
            username = content[0]
            key = content[1]
    else:
        with open(resource_path('settings.txt'), 'w', encoding='utf-8') as f:
            username = input('Username: ')
            key = input('Key: ')
            f.writelines("\n".join([username, key]))

    login_data = {'username': username, 'key': key, 'pc_id': get_uuid()}
    post_data(login_data)


def get_uuid():
    if platform.system() == 'Darwin':
        cmd = "system_profiler SPHardwareDataType | grep 'Serial Number' | awk '{print $4}'"
        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
        return result.stdout.strip().decode()
    else:
        return subprocess.check_output('wmic csproduct get UUID').decode().split()[1]


def post_data(data):
    try:
        response = requests.post('https://hermesbotserver.herokuapp.com/send_token', json=data)
        check_response(response)
    except:
        print('Server unavailable')


def check_response(response):
    if response.status_code == 200:
        print('Logged in successfully')
        read_tasks()
        Parallel(n_jobs=-1)(delayed(run_tasks)(i) for i in range(0, 1))
    elif response.status_code == 400:
        print('Request error')
    elif response.status_code == 401:
        print('Wrong password')
    elif response.status_code == 403:
        print('You can use Hermes Bot only on one PC. Contact support')
    elif response.status_code == 404:
        print('Username not found')
    else:
        print('Unknown error')


def read_tasks():
    with open(resource_path('tasks.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=',')
        for task in reader:
            tasks.append(task)


def run_tasks(task_num):
    driver = get_chromedriver(task_num)

    if is_login_needed:
        open_login_page(driver)
        autologin(driver, task_num)
    else:
        if is_link_from_monitor:
            wait_for_link(driver)
        else:
            open_product_page(driver)

        wait_for_product(driver)

        if is_any_size:
            get_sizes(driver)

        choose_size(driver)
        add_to_cart(driver)
        open_cart(driver)
        wait_for_the_end_of_queue(driver)
        place_order(driver, task_num)


def get_chromedriver(task_num):
    chrome_options = ChromeOptions()
    window_size = '700,700'
    chrome_options.add_argument(f'window-size={window_size}')
    user_data_dir = resource_path(f'chrome/Selenium_{task_num}')
    chrome_options.add_argument(f'user-data-dir={user_data_dir}')
    chrome_options.add_argument(f'profile-directory=Profile')
    chrome_options.add_experimental_option('detach', True)

    ext_file = resource_path(f'chrome/proxy_ext_{task_num}.zip')
    create_proxy_ext(ext_file)
    chrome_options.add_extension(ext_file)

    driver_path = resource_path('chrome/chromedriver_89')
    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def create_proxy_ext(ext_dir):
    proxy_file = resource_path('proxies.txt')
    with zipfile.ZipFile(ext_dir, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js(proxy_file))


def open_login_page(driver):
    login_url = f'https://{region}kith.com/account'
    driver.get(login_url)
    time.sleep(1)
    driver.get(login_url)


def find_element(driver, selector):
    element = driver.find_element_by_css_selector(selector)
    return element


def fill_form(form, string):
    form.clear()
    form.send_keys(string)


def autologin(driver, num):
    try:
        find_element(driver, paths['email']).send_keys(tasks[num]['email'])
        find_element(driver, paths['password']).send_keys(tasks[num]['password'])
        find_element(driver, paths['login_button']).click()
    except:
        print('Logged in')


def open_product_page(driver):
    driver.get(product_url)


def wait_for_link(driver):
    WebDriverWait(driver, 300).until(EC.url_contains('kith.com/products/'))


def wait_for_product(driver):
    try:
        wait = WebDriverWait(driver, 0.6)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, paths['sizes_box'])))
    except:
        driver.refresh()
        wait_for_product(driver)


def get_sizes(driver):
    combobox = find_element(driver, paths['sizes_box'])
    select = Select(combobox)
    sizes.clear()
    for option in select.options:
        size = option.get_attribute('value')
        sizes.append(size)


def choose_size(driver):
    value = random.choice(sizes)
    try:
        select_from_combobox(driver, paths['sizes_box'], value)
    except:
        print(f'Size {value} not found')
        sizes.remove(value)
        choose_size(driver)


def select_from_combobox(driver, combobox_selector, value):
    combobox = find_element(driver, combobox_selector)
    Select(combobox).select_by_value(value)


def add_to_cart(driver):
    find_element(driver, paths['add_to_cart_button']).click()


def open_cart(driver):
    cart_url = f'https://{region}kith.com/pages/international-checkout#Global-e_International_Checkout'
    driver.get(cart_url)


def wait_for_the_end_of_queue(driver):
    wait = WebDriverWait(driver, 300)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, paths['address_frame'])))
    while True:
        try:
            find_element(driver, paths['first_name']).click()
            break
        except:
            print('Waiting...')

        time.sleep(0.1)


def place_order(driver, num):
    autofill_billing(driver, num)

    if region:
        find_element(driver, paths['use_def_address']).click()
    else:
        find_element(driver, paths['use_alt_address']).click()
        autofill_shipping(driver, num)

    autofill_card(driver, num)
    # find_element(driver, select_paths['order_button']).click()


def autofill_billing(driver, num):
    fill_form(find_element(driver, paths['first_name']), tasks[num]['first_name'])
    fill_form(find_element(driver, paths['last_name']), tasks[num]['last_name'])
    fill_form(find_element(driver, paths['email_cart']), tasks[num]['email_cart'])
    select_from_combobox(driver, paths['country_box'], tasks[num]['country_box'])
    fill_form(find_element(driver, paths['address_line1']), tasks[num]['address_line1'])
    fill_form(find_element(driver, paths['address_line2']), tasks[num]['address_line2'])
    fill_form(find_element(driver, paths['city']), tasks[num]['city'])
    fill_form(find_element(driver, paths['postcode']), tasks[num]['postcode'])
    fill_form(find_element(driver, paths['mobile']), tasks[num]['mobile'])


def autofill_shipping(driver, num):
    fill_form(find_element(driver, paths['alt_first_name']), tasks[num]['alt_first_name'])
    fill_form(find_element(driver, paths['alt_last_name']), tasks[num]['alt_last_name'])
    select_from_combobox(driver, paths['alt_country_box'], tasks[num]['alt_country_box'])
    fill_form(find_element(driver, paths['alt_address_line1']), tasks[num]['alt_address_line1'])
    fill_form(find_element(driver, paths['alt_address_line2']), tasks[num]['alt_address_line2'])
    fill_form(find_element(driver, paths['alt_city']), tasks[num]['alt_city'])
    fill_form(find_element(driver, paths['alt_postcode']), tasks[num]['alt_postcode'])
    fill_form(find_element(driver, paths['alt_mobile']), tasks[num]['alt_mobile'])


def autofill_card(driver, num):
    payment_frame = find_element(driver, paths['payment_frame'])
    driver.switch_to.frame(payment_frame)
    find_element(driver, paths['card_number']).send_keys(tasks[num]['card_number'])
    find_element(driver, paths['exp_month']).send_keys(tasks[num]['exp_month'])
    find_element(driver, paths['exp_year']).send_keys(tasks[num]['exp_year'])
    find_element(driver, paths['cvv']).send_keys(tasks[num]['cvv'])


login()


# Windows
# pyinstaller -D -c --add-data "chrome/chromedriver_89.exe;chrome" -i "icons\icon.ico" -n "kith_bot" main.py
# C:\Users\macbook\AppData\Local\Temp

# Mac
# pyinstaller -w --add-data "chromedriver:." --add-data "icons/icon.PNG:icons" --add-data "fonts:fonts" -i "icons/icon.icns" -n "hermes_bot" mainwindow.py
# codesign -f -s "Certificate" /Users/macbook/Desktop/snkrs_bot/Sources/dist/hermes_bot.app --deep
