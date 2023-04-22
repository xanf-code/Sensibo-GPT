from sensibo import lowest_highest_ai, ac_details, set_ac_temp, test_gpt_op
from settings import is_debug_mode


def dynamic_ac_ai():
    global_json = ac_details()
    if is_debug_mode:
        print("DEBUG: TEST MODE")
        range = test_gpt_op["Temperature"]
    else:
        range = lowest_highest_ai(global_json["sensibo_data"][0]["temperature"], global_json["sensibo_data"]
                                  [0]["humidity"], global_json["sensibo_data"][0]["feelsLike"])
    set_ac_temp(range, global_json["sensibo_data"][0]["device_uid"])
