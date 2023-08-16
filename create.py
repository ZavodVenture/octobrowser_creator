from configparser import ConfigParser
from entities import Config, Error, Proxy, Wallet

config = ConfigParser()
config.read('config.ini')
config_object = Config(**config['settings'])

from progress.bar import Bar
from helpers import octobrowser, reader, chunks, worker
import colorama
from colorama import Fore
from typing import List
from time import sleep
from threading import Thread


API_URL = 'https://app.octobrowser.net/api/v2/automation/'
LOCAL_API_URL = 'http://localhost:58888/api/'


def init_exit():
    input('\nPress Enter to close the program...')
    exit()


def create_profiles(proxy_list: List[Proxy]):
    bar = Bar('Creating', max=config_object.profiles_number)

    bar.start()

    tag_creation = octobrowser.create_tag(config_object.tag_name)
    if isinstance(tag_creation, Error):
        bar.finish()
        return tag_creation

    ids = []

    for i in range(len(proxy_list)):
        title = f'{config_object.offset + i + 1}'

        result = octobrowser.create_profile(title, proxy_list[i], config_object.tag_name)
        if isinstance(result, Error):
            bar.finish()
            return result

        ids.append(result)
        bar.next()
        sleep(1)

    bar.finish()
    return ids


def launch_profiles(uuid_list):
    bar = Bar('Launching', max=config_object.profiles_number)
    bar.start()

    ws_list = []

    for uuid in uuid_list:
        result = octobrowser.run_profile(uuid)

        if isinstance(result, Error):
            bar.finish()
            return result

        ws_list.append(result)
        bar.next()
        sleep(3)

    bar.finish()
    return ws_list


def setup_profiles(ws_list, wallet_list: List[Wallet]):
    profile_tuple = [(ws_list[i], wallet_list[i]) for i in range(config_object.profiles_number)]
    profile_tuple = chunks(profile_tuple, config_object.thread_number)

    bar = Bar('Configuring', max=config_object.profiles_number)

    bar.start()

    for group in profile_tuple:
        threads = []
        for profile in group:
            ws, wallet = profile
            threads.append(Thread(target=worker, args=(ws, wallet, bar)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    bar.finish()


def main():
    print('Pre-launch verification...\n')

    wallet_list = reader.read_wallets()
    if isinstance(wallet_list, Error):
        print(wallet_list)
        init_exit()

    proxy_list = reader.read_proxy()
    if isinstance(proxy_list, Error):
        if proxy_list.error_type == 'File not found':
            proxy_list = [None] * len(wallet_list)
        else:
            print(proxy_list)
            init_exit()

    if len(wallet_list) != len(proxy_list):
        print(f'{Fore.RED}The number of proxies and wallets does not match{Fore.RESET}')
        init_exit()

    proxy_list = proxy_list[config_object.offset:config_object.offset + config_object.profiles_number]
    wallet_list = wallet_list[config_object.offset:config_object.offset + config_object.profiles_number]

    if len(proxy_list) != config_object.profiles_number:
        print(f'{Fore.RED}The number of profiles after the offset is less than the number of profiles specified in the settings{Fore.RESET}')
        init_exit()

    if None in proxy_list:
        print(f'{Fore.YELLOW}File {config_object.proxy_file} not found. Proxies will not be used.{Fore.RESET}\n')

    print(f'{Fore.GREEN}Verification is complete! Creating profiles...{Fore.RESET}\n')

    uuid_list = create_profiles(proxy_list)
    print()
    if isinstance(uuid_list, Error):
        print(uuid_list)
        init_exit()

    print(f'{Fore.GREEN}Profiles have been created! Launching profiles...{Fore.RESET}\n')

    ws_list = launch_profiles(uuid_list)
    print()
    if isinstance(ws_list, Error):
        print(ws_list)
        init_exit()

    print(f'{Fore.GREEN}Profiles have been successfully launched! Starting the setup process...{Fore.RESET}\n')

    setup_profiles(ws_list, wallet_list)

    print(f'\n{Fore.GREEN}All profiles are ready! Check for errors on them.{Fore.RESET}')
    init_exit()


if __name__ == '__main__':
    colorama.init()
    main()
