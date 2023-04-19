from flask import Flask, jsonify
from sensibo import main
from cron_ac_params import dynamic_ac_ai

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
