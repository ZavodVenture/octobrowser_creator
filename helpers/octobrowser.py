import requests
from entities import Proxy, Error
from create import config_object
import os

API_URL = 'https://app.octobrowser.net/api/v2/automation/'
LOCAL_API_URL = 'http://localhost:58888/api/'


def create_profile(title, proxy: Proxy, tag):
    request_data = {
        'title': title,
        'tags': [tag],
        'fingerprint': {
            'os': 'win'
        }
    }

    headers = {
        'X-Octo-Api-Token': config_object.api_token
    }

    if proxy:
        request_data['proxy'] = {
            'type': proxy.proxy_type,
            'host': proxy.ip,
            'port': proxy.port,
            'login': proxy.login,
            'password': proxy.password
        }

    try:
        r = requests.post(API_URL + 'profiles', json=request_data, headers=headers).json()
    except Exception as e:
        return Error('Profile creation error', 'An error occurred while processing the response from OctoBrowser', e)
    else:
        if not r.get('success'):
            return Error('Profile creation error', r)
        else:
            return r['data']['uuid']


def run_profile(uuid):
    metamask_path = os.path.abspath('nkbihfbeogaeaoehlefnkodbefgpgknn@10.34.3')

    request_data = {
        'uuid': uuid,
        'debug_port': True,
        'flags': [f'--load-extension={metamask_path}']
    }

    try:
        r = requests.post(LOCAL_API_URL + 'profiles/start', json=request_data).json()
    except Exception as e:
        return Error('Profile launching error', 'An error occurred while processing the response from OctoBrowser', e)
    else:
        if r.get('state') != 'STARTED':
            return Error('Profile launching error', r)
        else:
            return r.get('debug_port')


def check_tag(name):
    headers = {
        'X-Octo-Api-Token': config_object.api_token
    }

    try:
        r = requests.get(API_URL + 'tags', headers=headers).json()
    except Exception as e:
        return Error('Searching tag error', 'An error occurred while processing the response from OctoBrowser', e)
    else:
        if not r.get('success'):
            return Error('Searching tag error', r)
        else:
            found = False
            for i in r['data']:
                if i['name'] == name:
                    found = True
                    break
            return found


def create_tag(name):
    result = check_tag(name)
    if isinstance(result, Error) or result is True:
        return result

    request_data = {
        'name': name
    }

    headers = {
        'X-Octo-Api-Token': config_object.api_token
    }

    try:
        r = requests.post(API_URL + 'tags', json=request_data, headers=headers).json()
    except Exception as e:
        return Error('Creating tag error', 'An error occurred while processing the response from OctoBrowser', e)
    else:
        if not r.get('success'):
            return Error('Tag creating error', r)
        else:
            return True
