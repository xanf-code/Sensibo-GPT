import requests
import json
from dotenv import load_dotenv
import os

def turn_off_ac(device_id):
    load_dotenv()
    api_key  = os.environ.get('SENSIBO_API_KEY')
    ac_shutdown_endpoint = f'https://home.sensibo.com/api/v2/pods/{device_id}/acStates?apiKey={api_key}'

    payload = {
        'acState': {
            'on': False
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(ac_shutdown_endpoint, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print('AC shutdown request sent')
    else:
        print('Error sending AC shutdown request')
