import requests
import json
import time
from utils.turn_off_ac import turn_off_ac
from sensibo.sensibo import ac_details
from dotenv import load_dotenv
import os

load_dotenv()

family_id= os.environ.get('FAMILY_ID')
bearer_token= os.environ.get('TOKEN')
app_id= os.environ.get('APP_ID')

DOOR_STATUS_ENDPOINT = f'https://as-apia.coolkit.cc/v2/device/thing?familyid={family_id}&num=0'

headers = {
    'authority': 'as-apia.coolkit.cc',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en-IN;q=0.9,en-UM;q=0.8,en;q=0.7',
    'authorization': f'Bearer {bearer_token}',
    'origin': 'https://web.ewelink.cc',
    'referer': 'https://web.ewelink.cc/',
    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'x-ck-appid': app_id,
    'x-ck-nonce': 'AcpmedDq'
}

def check_door_status():
    r = requests.get(DOOR_STATUS_ENDPOINT,headers=headers)
    if r.status_code == 200:
        return r.json()["data"]["thingList"][0]["itemData"]["params"]["lock"] == 1
    else:
        return False

def poll_for_updates():
    while True:
        try:
            response = requests.get(DOOR_STATUS_ENDPOINT,headers=headers)
            for line in response.iter_lines():
                if line:
                    door_status = json.loads(line.decode('utf-8'))["data"]["thingList"][0]["itemData"]["params"]["lock"]
                    if door_status == 1:
                        global_json = ac_details()
                        ac_state = global_json["sensibo_data"][0]["ac_state"]
                        if ac_state:
                            print("Door is open. Waiting for 2 min...")
                            time.sleep(120)
                            response = requests.get(DOOR_STATUS_ENDPOINT,headers=headers)
                            door_status = json.loads(response.content.decode('utf-8'))["data"]["thingList"][0]["itemData"]["params"]["lock"]
                            if door_status == 1:
                                print("Door is still open. Turning off the AC.")
                                turn_off_ac(global_json["sensibo_data"][0]["device_uid"])
                            else:
                                print("Door was shut, AC state unchanged.")
        except:
            print("Error while polling.")
        time.sleep(10)
