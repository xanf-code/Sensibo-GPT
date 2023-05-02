import requests
import json

DOOR_STATUS_ENDPOINT = 'https://doorhandler.netlify.app/.netlify/functions/api/device/a4b000cd76'

def check_door_status():
    r = requests.get(DOOR_STATUS_ENDPOINT)
    if r.status_code == 200:
        return r.json()['status'] == 'open' 
    else:
        return False
