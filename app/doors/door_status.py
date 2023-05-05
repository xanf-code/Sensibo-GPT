import requests
import json
import time
from utils.turn_off_ac import turn_off_ac
from sensibo.sensibo import ac_details

DOOR_STATUS_ENDPOINT = 'https://doorhandler.netlify.app/.netlify/functions/api/device/a4b000cd76'

def check_door_status():
    r = requests.get(DOOR_STATUS_ENDPOINT)
    if r.status_code == 200:
        return r.json()['status'] == 'open' 
    else:
        return False

def poll_for_updates():
    while True:
        try:
            response = requests.get(DOOR_STATUS_ENDPOINT)
            for line in response.iter_lines():
                if line:
                    door_status = json.loads(line.decode('utf-8'))['status']
                    if door_status == "open":
                        global_json = ac_details()
                        ac_state = global_json["sensibo_data"][0]["ac_state"]
                        if ac_state:
                            print("Door is open. Waiting for 2 min...")
                            time.sleep(120)
                            response = requests.get(DOOR_STATUS_ENDPOINT)
                            door_status = json.loads(response.content.decode('utf-8'))['status']
                            if door_status == "open":
                                print("Door is still open. Turning off the AC.")
                                turn_off_ac(global_json["sensibo_data"][0]["device_uid"])
                            else:
                                print("Door was shut, AC state unchanged.")
        except:
            print("Error while polling for updates")
        time.sleep(10)
