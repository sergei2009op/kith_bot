import os, sys
import zipfile
import proxy
from selenium.webdriver import ChromeOptions, Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from joblib import Parallel, delayed


product_url = 'https://kith.com/account'


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


def create_proxy_ext(file_name):
    with zipfile.ZipFile(file_name, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js())


def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = ChromeOptions()
    window_size = '700,700'
    chrome_options.add_argument(f'window-size={window_size}')
    chrome_options.add_experimental_option('detach', True)

    if use_proxy:
        ext_file = 'proxy_auth_ext.zip'
        create_proxy_ext(ext_file)
        chrome_options.add_extension(ext_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver_path = resource_path('chromedriver_89')
    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def open_drivers():
    driver = get_chromedriver(use_proxy=True)
    driver.get(product_url)


Parallel(n_jobs=-1)(delayed(open_drivers)() for i in range(1, 3))
