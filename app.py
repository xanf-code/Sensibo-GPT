from sensibo import main, ac_details
from cron_ac_params import dynamic_ac_ai
from settings import MODE
import json

if MODE == "dev":
    from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route('/ac', methods=['POST'])
    def ac_toggle():
        main()
        response = jsonify({'message': '[INFO] AC toggle run.'})
        response.status_code = 200
        return response

    @app.route('/dynamic_ac', methods=['POST'])
    def dynamic_params():
        dynamic_ac_ai()
        response = jsonify({'message': '[INFO] Dynamic AC run.'})
        response.status_code = 200
        return response

    if __name__ == '__main__':
        app.run()

elif MODE == "prod":
    def lambda_handler(event, context):
        if event['rawPath'] == "/ac":
            main()
            return {"message": "[INFO] AC toggle run."}
        elif event['rawPath'] == "/dynamic_ac":
            dynamic_ac_ai()
            global_json = ac_details()
            ac_status = global_json["sensibo_data"][0]["ac_state"]
            if ac_status:
                return {"message": "[INFO] Dynamic AC run."}
            else:
                return {"message": "[INFO] AC turned off."}
        else:
            return {"message": "Invalid Endpoint"}
