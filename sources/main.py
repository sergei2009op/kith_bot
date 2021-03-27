import os, sys
import zipfile
import proxy
from selenium.webdriver import ChromeOptions, Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from joblib import Parallel, delayed

product_url = 'https://kith.com/account'

window_size = '700,700'
chrome_options = ChromeOptions()
# chrome_options.add_argument('headless')
chrome_options.add_argument('ignore-certificate-errors')
chrome_options.add_argument(f'window-size={window_size}')
chrome_options.add_experimental_option('detach', True)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path).replace('\\', '/')


driver_path = resource_path('chromedriver_89')


def get_chromedriver(use_proxy=False, user_agent=None):
    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", proxy.manifest_json)
            zp.writestr("background.js", proxy.combine_background_js())

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)

    driver = Chrome(executable_path=driver_path, options=chrome_options)
    return driver


def open_drivers():
    driver = get_chromedriver(use_proxy=True)
    driver.get(product_url)


Parallel(n_jobs=-1)(delayed(open_drivers)() for i in range(1, 3))
