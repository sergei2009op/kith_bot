import os, sys, time
import zipfile
import proxy
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
user_data_folder = resource_path('Selenium')
driver_path = resource_path('chromedriver_89')


def create_proxy_ext(file_name):
    with zipfile.ZipFile(file_name, 'w') as zp:
        zp.writestr("manifest.json", proxy.manifest_json)
        zp.writestr("background.js", proxy.combine_background_js())


def get_chromedriver(profile_num, use_proxy=False, user_agent=None):
    chrome_options = ChromeOptions()
    chrome_options.add_argument(f'window-size={window_size}')
    chrome_options.add_argument(f'user-data-dir={user_data_folder}')
    chrome_options.add_argument(f'profile-directory=Profile {profile_num}')
    chrome_options.add_experimental_option('detach', True)

    if use_proxy:
        ext_file = f'proxy_auth_ext_{profile_num}.zip'
        create_proxy_ext(ext_file)
        chrome_options.add_extension(ext_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def open_drivers(profile_num):
    product_url = 'https://kith.com/account'
    driver = get_chromedriver(profile_num, use_proxy=True)
    driver.get(product_url)


Parallel(n_jobs=-1)(delayed(open_drivers)(i) for i in range(1, 3))
