import requests
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("AC_API_KEY")
open_api_key = os.getenv("OPEN_AI_API_KEY")
openai.api_key = open_api_key

model_id = 'gpt-3.5-turbo'

url = f"https://home.sensibo.com/api/v2/users/me/pods?fields=*&apiKey={api_key}"

global_json = {}
is_debug_mode = False

test_gpt_op = {
    "Temperature": {
        "l": 23,
        "h": 27,
        "fanspeed": "medium"
    }
}


def ac_details():
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        room_data = [
            {
                "room_name": result["room"]["name"],
                "device_uid": result["smartMode"]["deviceUid"],
                "ac_state": result["acState"]["on"],
                "temperature": result["measurements"]["temperature"],
                "humidity": result["measurements"]["humidity"],
                "feelsLike": result["measurements"]["feelsLike"],
                "tvoc": result["measurements"]["tvoc"],
                "Co2": result["measurements"]["co2"],
            } for result in data["result"]]
        global_json = {"sensibo_data": room_data}
        return global_json
    else:
        print(f"Request failed with status code {response.status_code}")


def toggle_ac():
    global_json = ac_details()
    device_uid = global_json["sensibo_data"][0]["device_uid"]
    ac_state = False if global_json["sensibo_data"][0]["ac_state"] == True else True
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "acState": {
            "on": ac_state
        }
    }

    response = requests.post(
        f"https://home.sensibo.com/api/v2/pods/{device_uid}/acStates?apiKey={api_key}", headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        ac_status = "on" if global_json["sensibo_data"][0]["ac_state"] == False else "off"
        print(f"AC turned {ac_status} successfully.")
    else:
        print(f"Failed to turn on AC. Status code: {response.status_code}")


def lowest_highest_ai(temp, humidity, feels_like):
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
                                              {"role": "assistant", "content": f"What is the best AC configuration for a room with a temperature of {temp}°C, humidity of {humidity}%, feels-like temperature of {feels_like}°C, assuming there is only one person present in the room? Also, do not give me a sentence or such, just give me a json format so that i can use it in my web project. And i would want only one object in the JSON which will be called Temperature and three keys, namely l, h and fanspeed. The fanspeed can be low,medium,high or strong. Please note i want 0 words or sentences in the result, i would only expect a json object. Also only return the integer do not return anything like °C along with it."}])
    return completion.choices[0].message.content


def set_ac_temp(range, device_id):
    is_ac_on = get_ac_state()
    if is_ac_on:
        if is_debug_mode:
            low = range['l']
            high = range['h']
            fanspeed = range['fanspeed']
        else:
            json_obj = json.loads(range)
            low = json_obj['Temperature']['l']
            high = json_obj['Temperature']['h']
            fanspeed = json_obj['Temperature']['fanspeed']
        set_ac_param("targetTemperature", low, device_id)
        set_ac_param("fanLevel", fanspeed, device_id)
        set_ac_param("mode", "cool", device_id)
    else:
        print("Cannot set params, AC is off.")


def set_ac_param(param, newValue, device_id):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "newValue": newValue
    }
    response = requests.patch(
        f"https://home.sensibo.com/api/v2/pods/{device_id}/acStates/{param}?apiKey={api_key}", headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print(f"{param} : {newValue}")
    else:
        print("Something went wrong.")


def get_ac_state():
    get_ac_state = ac_details()
    ac_state = get_ac_state["sensibo_data"][0]["ac_state"]
    if ac_state == True:
        return True
    else:
        return False


def main():
    global_json = ac_details()
    toggle_ac()
    is_ac_on = get_ac_state()
    if is_ac_on:
        if is_debug_mode:
            print("DEBUG: TEST MODE")
            range = test_gpt_op["Temperature"]
        else:
            range = lowest_highest_ai(global_json["sensibo_data"][0]["temperature"], global_json["sensibo_data"]
                                      [0]["humidity"], global_json["sensibo_data"][0]["feelsLike"])
        set_ac_temp(range, global_json["sensibo_data"][0]["device_uid"])
    else:
        print("AC in off state, not getting data. ")


# main()
