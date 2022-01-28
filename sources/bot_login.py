import file_handling as fh
import os, subprocess, platform
import requests


def get_uuid():
    if platform.system() == 'Darwin':
        cmd = "system_profiler SPHardwareDataType | grep 'Serial Number' | awk '{print $4}'"
        result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
        return result.stdout.strip().decode()
    else:
        return subprocess.check_output('wmic csproduct get UUID').decode().split()[1]


class Login(object):
    def __init__(self):
        self.status = 0

    def check_status(self, status):
        match status:
            case 200:
                self.status = 1
                return 'Logged in successfully'
            case 400:
                return 'Request error'
            case 401:
                return 'Wrong password'
            case 403:
                return 'You can use Bot only on one PC. Contact support'
            case 404:
                return 'Username not found'
            case _:
                return 'Unknown error'

    def post_data(self, data):
        try:
            response = requests.post(f'https://{os.environ["DOMAIN"]}.herokuapp.com/send_token', json=data)
            print(self.check_status(response.status_code))
        except:
            print('Server unavailable')

    def login(self):
        data_file = '../bot_data/login_info.txt'

        try:
            content = fh.read_file(data_file)
            username = content[0]
            key = content[1]
        except:
            username = input('Username: ')
            key = input('Key: ')
            fh.write_file(data_file, [username, key])

        login_data = {'username': username, 'key': key, 'pc_id': get_uuid()}
        self.post_data(login_data)
