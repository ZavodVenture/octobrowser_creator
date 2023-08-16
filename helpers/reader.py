from entities import Wallet, Proxy, Error
from create import config_object


def read_proxy():
    try:
        filename = config_object.proxy_file

        with open(filename, encoding='utf-8') as file:
            proxy_raw = file.read().split('\n')
            if not proxy_raw[-1]:
                proxy_raw = proxy_raw[:-1]
            file.close()

        result = []

        for proxy in proxy_raw:
            result.append(Proxy(config_object.proxy_type, *proxy.split(':')))

        return result
    except FileNotFoundError:
        return Error('File not found', 'Proxy file not found')
    except Exception as e:
        return Error('Proxy reading error', 'Couldn\'t read proxy list from file', e)


def read_wallets():
    try:
        filename = config_object.metamask_file

        with open(filename, encoding='utf-8') as file:
            seeds_raw = file.read().split('\n')
            if not seeds_raw[-1]:
                seeds_raw = seeds_raw[:-1]
            file.close()

        result = []

        for seed in seeds_raw:
            result.append(Wallet(seed))

        return result
    except Exception as e:
        return Error('Wallets reading error', 'Couldn\'t read wallets list from file', e)
