from sensibo import lowest_highest_ai, ac_details, set_ac_temp, is_debug_mode, test_gpt_op


def dynamic_ac_ai():
    global_json = ac_details()
    ac_status = global_json["sensibo_data"][0]["ac_state"]
    if ac_status:
        if is_debug_mode:
            print("DEBUG: TEST MODE")
            range = test_gpt_op["Temperature"]
        else:
            range = lowest_highest_ai(global_json["sensibo_data"][0]["temperature"], global_json["sensibo_data"]
                                      [0]["humidity"], global_json["sensibo_data"][0]["feelsLike"])
        set_ac_temp(range, global_json["sensibo_data"][0]["device_uid"])
    else:
        print("Cannot update, AC off.")
