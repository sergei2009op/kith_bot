import random

manifest_json = '''
{
  "version": "1.0.0",
  "manifest_version": 2,
  "name": "Chrome Proxy",
  "permissions": [
    "proxy",
    "tabs",
    "unlimitedStorage",
    "storage",
    "<all_urls>",
    "webRequest",
    "webRequestBlocking"
  ],
  "background": {
    "scripts": ["background.js"]
  },
  "minimum_chrome_version":"22.0.0"
}
'''

background_js = '''
var config = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
    }
};

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn, {urls: ["<all_urls>"]}, ["blocking"]
);
'''


def get_random_proxy():
    with open('proxies.txt') as f:
        proxies = f.read().splitlines()

    proxy = random.choice(proxies).split(':')
    host = proxy[0]
    port = proxy[1]
    user = proxy[2]
    password = proxy[3]

    return host, port, user, password


def combine_background_js():
    return background_js % get_random_proxy()
