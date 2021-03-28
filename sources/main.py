import os, sys, zipfile
import proxy
from xpaths import xpaths
from selenium.webdriver import ChromeOptions, Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from joblib import Parallel, delayed


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


window_size = '700,700'
driver_path = resource_path('chromedriver_89')


def create_proxy_ext(ext_dir):
    with zipfile.ZipFile(ext_dir, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js())


def get_chromedriver(dir_num, use_proxy=False, user_agent=None):
    chrome_options = ChromeOptions()
    chrome_options.add_argument(f'window-size={window_size}')

    user_data_dir = f'Selenium_{dir_num}'
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


def open_drivers(dir_num):
    driver = get_chromedriver(dir_num, use_proxy=True)
    open_login_page(driver)


def fill_form_with_chars(form, string):
    form.click()
    form.clear()
    form.send_keys([chars for chars in string])


def open_login_page(driver):
    login_url = 'https://eu.kith.com/account'
    driver.get(login_url)

    email = driver.find_element_by_id('CustomerEmail')
    password = driver.find_element_by_id('CustomerPassword')

    fill_form_with_chars(email, 'aaaa@mail.ru')
    fill_form_with_chars(password, 'aaaaaaa')

    button = driver.find_element_by_xpath(xpaths['login_button'])
    button.click()


Parallel(n_jobs=-1)(delayed(open_drivers)(i) for i in range(1, 3))
