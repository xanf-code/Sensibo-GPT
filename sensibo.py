import requests
import json
import openai
import os
from dotenv import load_dotenv
from open_weather import get_hourly_weather_data
import datetime
import math
from settings import MODE, is_debug_mode
from air_quality import calculate_air_quality

load_dotenv()

if MODE == "dev":
    api_key = os.getenv("AC_API_KEY")
    open_api_key = os.getenv("OPEN_AI_API_KEY")
    weather_api = os.getenv("WEATHER_API")
elif MODE == "prod":
    api_key = os.environ.get('SENSIBO_API_KEY')
    open_api_key = os.environ.get('OPEN_API_KEY')
    weather_api = os.environ.get('WEATHER_API_KEY')

openai.api_key = open_api_key

model_id = 'gpt-3.5-turbo'

url = f"https://home.sensibo.com/api/v2/users/me/pods?fields=*&apiKey={api_key}"

global_json = {}

test_gpt_op = {
    "Temperature": {
        "l": 20,
        "h": 26,
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
                "anti_mold_enabled":result["antiMoldConfig"]["enabled"],
                "anti_mold_time":result["antiMoldConfig"]["fan_time"],
                "anti_mold_running":result["antiMoldConfig"]["anti_mold_running"],
                "acUsage": result["acUsage"]
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
                                              {"role": "assistant", "content": f"What is the best AC configuration for a room with a temperature of {temp}°C, humidity of {humidity}%, feels-like temperature of {feels_like}°C, assuming there is only one person present in the room? Also, do not give me a sentence or such, just give me a json format so that i can use it in my web project. And i would want only one object in the JSON which will be called Temperature and four keys, namely l, h, fanspeed, mode. The l is what you feel is the desired lowest temperature and h is what you feel is the desired highest temperature. The fanspeed can be quiet,low,medium_low,medium,high or strong. The mode can be cool, heat, fan, dry, auto. Please note i want 0 words or sentences in the result, i would only expect a json object. Also only return the integer do not return anything like °C along with it."}])
    return completion.choices[0].message.content


def calculate_best_temperature(high_temp, low_temp):
    global_json = ac_details()
    current_temp = global_json["sensibo_data"][0]["temperature"]
    humidity = global_json["sensibo_data"][0]["humidity"]
    tvoc = global_json["sensibo_data"][0]["tvoc"]
    co2 = global_json["sensibo_data"][0]["Co2"]
    air_quality = calculate_air_quality(tvoc, co2)
    current_time = datetime.datetime.now().time()

    dew_point = current_temp - ((100 - humidity)/5)

    apparent_temp = current_temp + 0.5 * \
        (6.105*math.exp(17.27*dew_point/(dew_point+237.7))*(humidity/100)-10)

    if apparent_temp < 0:
        desired_temp_range = (23, 25)
    elif apparent_temp < 10:
        desired_temp_range = (24, 26)
    elif apparent_temp < 20:
        desired_temp_range = (25, 27)
    elif apparent_temp < 30:
        desired_temp_range = (26, 28)
    elif apparent_temp < 40:
        desired_temp_range = (27, 29)
    else:
        desired_temp_range = (28, 30)

    if current_time >= datetime.time(22, 0) or current_time < datetime.time(6, 0):
        desired_temp_range = (
            desired_temp_range[0] - 1, desired_temp_range[1] - 1)

    if air_quality > 150:
        desired_temp_range = (
            desired_temp_range[0] + 1, desired_temp_range[1] + 1)

    forecast_temp = get_hourly_weather_data(weather_api)
    if forecast_temp > current_temp + 5:
        desired_temp_range = (
            desired_temp_range[0] + 1, desired_temp_range[1] + 1)
    elif forecast_temp < current_temp - 5:
        desired_temp_range = (
            desired_temp_range[0] - 1, desired_temp_range[1] - 1)

    if high_temp > desired_temp_range[1]:
        high_temp = desired_temp_range[1]
    if low_temp < desired_temp_range[0]:
        low_temp = desired_temp_range[0]
    target_temp = (high_temp + low_temp) / 2
    temp_diff = target_temp - current_temp
    if temp_diff > 0:
        result_temp = target_temp - temp_diff
    else:
        result_temp = target_temp + abs(temp_diff)
    if result_temp > high_temp:
        return high_temp
    elif result_temp < low_temp:
        return low_temp
    else:
        return round(result_temp)


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
            mode = json_obj['Temperature']['mode']
        best_target_temp = calculate_best_temperature(
            high_temp=high, low_temp=low)
        set_ac_param("targetTemperature", best_target_temp, device_id)
        set_ac_param("fanLevel", fanspeed, device_id)
        set_ac_param("mode", mode, device_id)
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
