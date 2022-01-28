from bot_login import Login
import file_handling as fh
import proxy
from paths import paths
import sys, platform, re, zipfile, time, random
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
import joblib as jl


def get_chromedriver(task_num):
    chrome_options = ChromeOptions()
    window_size = '700,700'
    chrome_options.add_argument(f'window-size={window_size}')
    user_data_dir = fh.resource_path(f'chrome/Selenium/Selenium_{task_num}')
    chrome_options.add_argument(f'user-data-dir={user_data_dir}')
    chrome_options.add_argument(f'profile-directory=Profile')
    chrome_options.add_experimental_option('detach', True)

    ext_file = fh.resource_path(f'chrome/proxies/proxy_{task_num}.zip')
    create_proxy_ext(ext_file)
    chrome_options.add_extension(ext_file)

    driver_path = fh.resource_path(f'chrome/{platform.system()}/chromedriver')
    driver = Chrome(executable_path=driver_path, options=chrome_options)

    return driver


def create_proxy_ext(ext_dir):
    proxy_file = fh.resource_path('../bot_data/proxies.txt')
    with zipfile.ZipFile(ext_dir, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js(proxy_file))


def find_element(driver, selector):
    element = driver.find_element(by=By.CSS_SELECTOR, value=selector)

    return element


def wait_for_link(driver):
    WebDriverWait(driver, 300).until(EC.url_contains('kith.com/products/'))


def wait_for_product(driver):
    try:
        wait = WebDriverWait(driver, 0.6)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, paths['add_to_cart_button'])))
    except:
        driver.refresh()
        wait_for_product(driver)


def items_of_container(driver, value):
    try:
        container = find_element(driver, paths[f'sizes_box_1'])
        items = container.find_elements(by=By.TAG_NAME, value='option')
    except:
        container = find_element(driver, paths[f'sizes_box_2'])
        items = container.find_elements(by=By.TAG_NAME, value=value)

    return items


def wait_in_queue(driver):
    wait = WebDriverWait(driver, 3000)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, paths['address_frame'])))

    while True:
        try:
            find_element(driver, paths['first_name']).click()
            break
        except:
            time.sleep(0.1)


def fill_form(form, string):
    form.clear()
    form.send_keys(string)


def select_country(driver, selector, country):
    combobox = find_element(driver, selector)
    Select(combobox).select_by_visible_text(country)


class KithBot(object):
    def __init__(self):
        self.tasks = [{}]
        self.is_login = False
        self.is_manual = False
        self.is_any_size = False
        self.region = ''
        self.product_id = ''
        self.preset_sizes = []
        self.available_sizes = []

    def start(self):
        self.init()
        self.read_tasks()
        jl.Parallel(n_jobs=-1)(jl.delayed(self.run_tasks)(i) for i in range(0, jl.cpu_count()))
        sys.exit(0)

    def read_tasks(self):
        content = fh.read_file('../bot_data/tasks.csv')
        self.tasks.clear()
        for task in content:
            self.tasks.append(task)

    def init(self):
        content = fh.read_file('../bot_data/init.txt')
        content = [re.sub(r'\s+', '', s).split(':')[1] for s in content]

        self.set_region(content[0].lower())
        self.is_login = bool(int(content[1]))
        self.is_manual = bool(int(content[2]))
        self.is_any_size = bool(int(content[3]))
        self.product_id = content[4]
        self.preset_sizes = content[5].split(',')

    def set_region(self, content):
        if content not in ['eu', 'us']:
            print('Unknown region')
            sys.exit(2)
        elif content == 'eu':
            self.region = 'eu.'

    def run_tasks(self, task_num):
        driver = get_chromedriver(task_num)

        if self.is_login:
            self.account_login(driver, task_num)
        else:
            self.open_product_page(driver)
            self.choose_size(driver)
        self.open_cart(driver)
        self.place_order(driver, task_num)

    def account_login(self, driver, num):
        self.open_login_page(driver)

        try:
            find_element(driver, paths['email']).send_keys(self.tasks[num]['email'])
            find_element(driver, paths['password']).send_keys(self.tasks[num]['password'])
            find_element(driver, paths['login_button']).click()
            print(f'Logged in into the account {num}')
        except:
            print('You have already been logged in')

    def open_login_page(self, driver):
        login_url = f'https://{self.region}kith.com/account'
        driver.get(login_url)
        driver.refresh()

    def open_product_page(self, driver):
        if self.is_manual:
            wait_for_link(driver)
        else:
            product_url = f'https://{self.region}kith.com/products/{self.product_id}'
            driver.get(product_url)
            wait_for_product(driver)

    def choose_size(self, driver):
        try:
            size = random.choice(self.get_suitable_sizes(driver))
            self.select_size(driver, size)
            find_element(driver, paths['add_to_cart_button']).click()
        except:
            print('Sizes not available. Picking available size')
            self.is_any_size = True
            self.choose_size(driver)

    def get_suitable_sizes(self, driver):
        self.get_available_sizes(driver)

        if self.is_any_size:
            suitable_sizes = self.available_sizes
        else:
            suitable_sizes = list(set(self.available_sizes) & set(self.preset_sizes))

        return suitable_sizes

    def get_available_sizes(self, driver):
        self.available_sizes.clear()
        items = items_of_container(driver, value='input')

        for item in items:
            value = item.get_attribute('value')
            if value != 'null':
                self.available_sizes.append(value)

    def select_size(self, driver, size):
        items = items_of_container(driver, value='li')
        index = self.available_sizes.index(size) - len(self.available_sizes)
        items[index].click()

    def open_cart(self, driver):
        time.sleep(0.5)
        cart_url = f'https://{self.region}kith.com/pages/international-checkout'
        driver.get(cart_url)
        wait_in_queue(driver)

    def place_order(self, driver, num):
        self.autofill_billing(driver, num)
        find_element(driver, paths['use_def_address']).click()
        # find_element(driver, paths['use_alt_address']).click()
        # self.autofill_shipping(driver, num)
        self.autofill_card(driver, num)
        find_element(driver, paths['order_button']).click()

        try:
            find_element(driver, paths['confirm_button']).click()
        except:
            print('No need to confirm')

    def autofill_billing(self, driver, num):
        fill_form(find_element(driver, paths['first_name']), self.tasks[num]['first_name'])
        fill_form(find_element(driver, paths['last_name']), self.tasks[num]['last_name'])
        fill_form(find_element(driver, paths['email_cart']), self.tasks[num]['email_cart'])
        select_country(driver, paths['country_box'], self.tasks[num]['country'])
        fill_form(find_element(driver, paths['address_line1']), self.tasks[num]['address_line1'])
        fill_form(find_element(driver, paths['address_line2']), self.tasks[num]['address_line2'])
        fill_form(find_element(driver, paths['city']), self.tasks[num]['city'])
        fill_form(find_element(driver, paths['postcode']), self.tasks[num]['postcode'])
        fill_form(find_element(driver, paths['mobile']), self.tasks[num]['mobile'])

    # def autofill_shipping(self, driver, num):
    #     fill_form(find_element(driver, paths['alt_first_name']), self.tasks[num]['first_name'])
    #     fill_form(find_element(driver, paths['alt_last_name']), self.tasks[num]['last_name'])
    #     select_country(driver, paths['alt_country_box'], self.tasks[num]['country'])
    #     fill_form(find_element(driver, paths['alt_address_line1']), self.tasks[num]['address_line1'])
    #     fill_form(find_element(driver, paths['alt_address_line2']), self.tasks[num]['address_line2'])
    #     fill_form(find_element(driver, paths['alt_city']), self.tasks[num]['city'])
    #     fill_form(find_element(driver, paths['alt_postcode']), self.tasks[num]['postcode'])
    #     fill_form(find_element(driver, paths['alt_mobile']), self.tasks[num]['mobile'])

    def autofill_card(self, driver, num):
        payment_frame = find_element(driver, paths['payment_frame'])
        driver.switch_to.frame(payment_frame)
        find_element(driver, paths['card_number']).send_keys(self.tasks[num]['card_number'])
        find_element(driver, paths['exp_month']).send_keys(self.tasks[num]['exp_month'])
        find_element(driver, paths['exp_year']).send_keys(self.tasks[num]['exp_year'])
        find_element(driver, paths['cvv']).send_keys(self.tasks[num]['cvv'])
        driver.switch_to.parent_frame()


if __name__ == '__main__':
    login = Login()
    login.login()

    if login.status:
        bot = KithBot()
        bot.start()

    sys.exit(1)
