from sensibo.sensibo import main,ac_details
from crons.cron_ac_params import dynamic_ac_ai
import json
from flask import Flask, jsonify
from bill.cost_calculator import calculate_ac_bill
from bill.mail_bill_service import email_bill

app = Flask(__name__)


@app.route('/ac', methods=['POST'])
def ac_toggle():
    main()
    response = jsonify({'message': '[INFO] AC toggle run.'})
    response.status_code = 200
    return response


@app.route('/dynamic_ac', methods=['POST'])
def dynamic_params():
    global_json = ac_details()
    ac_status = global_json["sensibo_data"][0]["ac_state"]
    if ac_status:
        dynamic_ac_ai()
        response = jsonify({'message': '[INFO] Dynamic AC run.'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'message': '[INFO] Cannot update, AC off.'})
        response.status_code = 200
        return response

@app.route('/usage', methods=['GET'])
def ac_usage():
    global_json = ac_details()
    usage = global_json["sensibo_data"][0]["acUsage"]
    hours,bill = calculate_ac_bill(usage_seconds=usage)
    rounded_hours = round(hours,2)
    email_bill(rounded_hours, bill)
    response = jsonify({'message': 'Email sent successfully.'})
    response.status_code = 200
    return response

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0',port=8080)
