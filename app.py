from flask import Flask
from sensibo import main
from cron_ac_params import dynamic_ac_ai

app = Flask(__name__)


@app.route('/ac', methods=['POST'])
def ac_toggle():
    main()
    return "[INFO] AC toggle run."


@app.route('/dynamic_ac', methods=['POST'])
def dynamic_params():
    dynamic_ac_ai()
    return "[INFO] Dynamic AC run."


if __name__ == '__main__':
    app.run()
