from web3 import Web3
import time
import requests
from fake_useragent import UserAgent
from eth_account.messages import encode_defunct
import random
from pathlib import Path

from inputs.config import config

class Plume:
    def __init__(self, key, proxy) -> None:
        self.web3 = Web3()

        self.privatekey = key
        self.account = self.web3.eth.account.from_key(self.privatekey)
        self.address = self.account.address
        
        self.plume_session = requests.Session()
        self.proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'} if proxy and proxy != '' else {}
        self.plume_session.proxies.update(self.proxies)
        self.plume_cookies = {}

        self.ua = UserAgent().chrome

    def check_status(self):
        try:
            URL = 'https://registration.plumenetwork.xyz/api/sign-read'
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'priority': 'u=1, i',
                'referer': 'https://registration.plumenetwork.xyz/',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self.ua,
            }

            params = {
                'address': self.address,
            }

            response = self.send_request(self.plume_session, URL, headers=headers, params=params, method='get')
            return response.json()['registered']
        except Exception as error:
            print(f'Error: {error}')
            return None

    def register(self):
        try:
            URL = 'https://registration.plumenetwork.xyz/api/sign-write'
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://registration.plumenetwork.xyz',
                'priority': 'u=1, i',
                'referer': 'https://registration.plumenetwork.xyz/',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self.ua,
            }
            
            message_ = "By signing this message, I confirm that I have read and agreed to Plume's Airdrop Terms of Service. This does not cost any gas to sign."
            signature_ = self.get_signature(message_)

            json_data = {
                'message': message_,
                'signature': signature_,
                'address': self.address,
                'twitterEncryptedUsername': None,
                'twitterEncryptedId': None,
                'discordEncryptedUsername': None,
                'discordEncryptedId': None,
            }

            response = self.send_request(self.plume_session, URL, headers=headers, json_data=json_data, method='post')
            return True
        except Exception as error:
            print(f'Error: {error}')
            return None
    
    def send_request(self, session, URL, headers=None, json_data=None, cookies=None, params=None, data=None, allow_redirects=None, method: str = None):
        for _ in range(1):
            try:
                if method.lower() == 'post':
                    response = session.post(url=URL, headers=headers, json=json_data, cookies=cookies, params=params, data=data, allow_redirects=allow_redirects)
                    if response.ok:
                        return response
                    else:
                        print(response.text)
                elif method.lower() == 'get':
                    response = session.get(url=URL, headers=headers, cookies=cookies, params=params, data=data, allow_redirects=allow_redirects)
                    if response.ok:
                        return response
                    else:
                        print(response.text)
            except:
                time.sleep(1)
                pass
        
        return None
    
    def get_signature(self, message_text: str):
        try:
            message = encode_defunct(text=message_text)
            sign = self.web3.eth.account.sign_message(message, private_key=self.privatekey)
            signature = self.web3.to_hex(sign.signature)
            
            return signature
        except Exception as error:
            print(f'Error: {error}')
            return 0
def check_and_create_dir(file_path: Path):
    if file_path.is_file():
        pass
    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()
    return None
    
if __name__ == '__main__':
    with open('inputs/private_keys.txt', 'r') as file:
        private_keys = file.read().splitlines()
    
    with open('inputs/proxies.txt', 'r') as file:
        proxies = file.read().splitlines()
    
    accounts = list(zip(private_keys, proxies))
    check_and_create_dir(Path('./results/success.txt'))
    check_and_create_dir(Path('./results/failed.txt'))
    
    if config['TO_SHUFFLE']:
        random.shuffle(accounts)

    for account in accounts:
        try:
            key, proxy = account
            plume = Plume(key, proxy)
            print(f'###=###=###=###\n{plume.address} — working\n###=###=###=###')
            
            register_status = plume.check_status()
            if not register_status:
                plume.register()

                register_status = plume.check_status()
                if register_status:
                    print('Successfully completed registration')
                    with open('results/success.txt', 'a') as file:
                        file.write(f'{plume.privatekey}\n')
                else:
                    print('Failed')
                    with open('results/failed.txt', 'a') as file:
                        file.write(f'{plume.privatekey}\n')
            else:
                print('Registration already completed')
                with open('results/success.txt', 'a') as file:
                    file.write(f'{plume.privatekey}\n')
            
            to_sleep = random.uniform(*config['DELAY_ACCS'])
            print(f'Sleep {round(to_sleep, 2)} sec')
            time.sleep(to_sleep)

        except Exception as error:
            print(f'{plume.address} | Error: {error}')

            with open('results/failed.txt', 'a') as file:
                file.write(f'{plume.privatekey}\n')

            to_sleep = random.uniform(*config['DELAY_ACCS'])
            print(f'Sleep {round(to_sleep, 2)} sec')
            time.sleep(to_sleep)
