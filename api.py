import requests
import json
import base64
import time
import datetime

# CONFIG

from config import Config

API_TOKEN = Config.BOT_TOKEN
SHORTENER_DOMAIN = Config.SHORTENER_DOMAIN
EXT_TOKEN = Config.EXT_TOKEN
ADMIN_IDS = Config.ADMIN_IDS

def cr_token():

    parts = EXT_TOKEN.split(".")
    
    p_b64dec = base64.b64decode(parts[1]+'==').decode('utf-8')
    
    payload = json.loads(p_b64dec)
    payload.update({'exp': int(time.time())+20000})
    payload = json.dumps(payload)
    
    p_b64enc = base64.b64encode(payload.encode('UTF-8'))
    
    bearer = parts[1] + "." + str(p_b64enc.decode('UTF-8').rstrip('='))
    
    return bearer

def access_api():
    api_url = f'{SHORTENER_DOMAIN.rstrip("/")}/api'

    headers = {
        'accept' : '*/*',
        'authorization': f'Bearer {cr_token()}'
    }

    response = requests.get(api_url, headers=headers)

    if response.json()['status'] == 'success':
        return 1
    else:
        return 0

def short_url(long_url, short_url):
    api_url = f'{SHORTENER_DOMAIN.rstrip("/")}/api/create'

    headers = {
        'accept' : '*/*',
        'authorization': f'Bearer {cr_token()}'
    }

    json_data = {
        'shortName': short_url,
        'url': long_url
    }

    response = requests.post(api_url, headers=headers, json=json_data)

    return response.json()

def delete_url(short_url):
    api_url = f'{SHORTENER_DOMAIN.rstrip("/")}/api/delete'

    headers = {
        'accept' : '*/*',
        'authorization': f'Bearer {cr_token()}'
    }

    json_data = {
        'shortName': short_url
    }

    response = requests.post(api_url, headers=headers, json=json_data)

    return response.json()

def list_url():
    api_url = f'{SHORTENER_DOMAIN.rstrip("/")}/api/list'

    headers = {
        'accept' : '*/*',
        'authorization': f'Bearer {cr_token()}'
    }

    response = requests.get(api_url, headers=headers)

    return response.json()

def check_url_exist(short_url):
    api_url = f'{SHORTENER_DOMAIN.rstrip("/")}/api/list'

    headers = {
        'accept' : '*/*',
        'authorization': f'Bearer {cr_token()}'
    }

    response = requests.get(api_url, headers=headers)

    list_shorts = [x['shortName'] for x in response.json()['result']]

    if str(short_url) in list_shorts:
        return True
    else:
        return False

def readable_time(unix_time):
    return datetime.datetime.fromtimestamp(int(str(unix_time)[:10])).strftime('%Y-%m-%d %H:%M:%S')