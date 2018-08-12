import os

from flask import Flask
import json

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    #app.config.from_mapping(
    #    SECRET_KEY='dev',
    #    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    #)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    hardwareDispatch = {
        'servo1' : lambda: getServoStatus(1),
        'servo2' : lambda: getServoStatus(2),
        'servo3' : lambda: getServoStatus(3),
        'servo4' : lambda: getServoStatus(4),
        'servo5' : lambda: getServoStatus(5),
        'ultrasound' : lambda: getUltraSoundStatus(),
        'camera' : lambda: getCameraStatus(),
        }

    configDispatch = {
        'uss_pid' : lambda: getPIDsetting('uss_pid'),
        'facedetection_pid_x': lambda: getPIDsetting('facedetection_pid_x'),
        'facedetection_pid_y': lambda: getPIDsetting('facedetection_pid_y'),
        }

    @app.route('/')
    def home():
        # TODO some useful content
        return 'Home'

    @app.route('/status/<string:id>', methods=('GET',))
    def status(id):
        if id in hardwareDispatch:
            return hardwareDispatch[id]()
        else:
            reply = {
                "error":"Resource not found!"
            }
            return json.dumps(reply)

    @app.route('/config/<string:id>', methods=('GET','POST'))
    def config(id):
        if request.method is 'POST':
            Kp = request.form["Kp"]
            Ki = request.form["Ki"]
            Kd = request.form["Kd"]
            setPIDsetting(id, Kp, Ki, Kd)
        else:
            if id in configDispatch:
                return configDispatch[id]()

    def getServoStatus(servo_id):
        # return the servo angle for servo with id
        # TODO get the status via zmq
        placeholder_reply = {
            "name": f"servo{servo_id}",
            "angle": 90+servo_id
            }
        return json.dumps(placeholder_reply)

    def getUltraSoundStatus():
        # return the measured distance (time, distance)
        # TODO get the status via zmq
        placeholder_reply = {
            "name":"ultrasound",
            "distance":8
            }
        return json.dumps(placeholder_reply)

    def getCameraStatus():
        # return the image with detected feature highlights
        # TODO get the status via zmq
        return 'some image'

    def getPIDsetting(pid_id):
        # TODO get the status via zmq
        placeholder_reply = {
            "Kp":0,1
            "Ki":0,2
            "Kd":0,3
            }
        return json.dump(placeholder_reply)

    def setPIDsetting(pid_id):
        # TODO send the new status via zmq
        pass

    return app
