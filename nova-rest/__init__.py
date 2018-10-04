import os
from flask import Flask
from flask import Response
from flask import request
import json
import zmq
#from communication.zmq_status_sub_communication import StatusPublishSubCommunication

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

    status_comm = StatusPublishSubCommunication()
    api_command_comm = APICommandReqCommunication()

    hardwareDispatch = {
        'servo1' : lambda: getServoStatus('servo1'),
        'servo2' : lambda: getServoStatus('servo2'),
        'servo3' : lambda: getServoStatus('servo3'),
        'servo4' : lambda: getServoStatus('servo4'),
        'servo5' : lambda: getServoStatus('servo5'),
        'ultrasound' : lambda: getUltraSoundStatus(),
        'camera' : lambda: getCameraStatus(),
        }

    configDispatch = {
        'distance_pid' : lambda: getPIDsetting('distance_pid'),
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
            body = {
                "id":f"{id}",
                "error":"Resource not found!"
            }
            resp = Response(json.dumps(body))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

    @app.route('/config/<string:id>', methods=('GET','POST'))
    def config(id):
        if request.method is 'POST':
            Kp = request.form["Kp"]
            Ki = request.form["Ki"]
            Kd = request.form["Kd"]
            setPIDsetting(id, Kp, Ki, Kd)
        elif request.method is 'GET':
            if id in configDispatch:
                return configDispatch[id]()
        else:
            body = {
                "id":f"{id}",
                "error":"Config item not found!"
            }
            resp = Response(json.dumps(body))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp

    @app.route('/test/<string:id>', methods=('GET',))
    def test(id):
        id = int(id)
        cmd = (0,0,int(id),0,0)
        api_command_comm.sendCommand(cmd)

        body = {
            "id":f"{cmd}",
            "message":"Seems to have gone well!"
        }
        resp = Response(json.dumps(body))
        return resp

    def getServoStatus(servo_id):
        # return the servo angle for servo with id
        #(id, (angle,arg2,arg3)) = status_comm.getStatus(servo_id)
        (id, angle) = status_comm.getStatus(servo_id)

        body = {
            "id": f"{id}",
            "value": f"{angle}"
            }
        resp = Response(json.dumps(body))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def getUltraSoundStatus():
        # return the measured distance (time, distance)
        #(id, (distance,arg2,arg3)) = status_comm.getStatus('ultrasound')
        (id, distance) = status_comm.getStatus('ultrasound')
        body = {
            "id":f"{id}",
            "value":f"{distance}"
            }
        resp = Response(json.dumps(body))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def getCameraStatus():
        # return the image with detected feature highlights
        # TODO get the status via zmq
        body = {
            "content":"some image"
            }
        resp = Response(json.dumps(body))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def getPIDsetting(pid_id):
        # TODO get the status via zmq
        body = {
            "id":f"{pid_id}",
            "Kp":0.1,
            "Ki":0.2,
            "Kd":0.3
            }
        resp = Response(json.dumps(body))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def setPIDsetting(pid_id):
        # TODO send the new status via zmq
        pass

    return app

class StatusPublishSubCommunication:
    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        self.socket.connect("tcp://localhost:8888")
        self.socket.setsockopt(zmq.SUBSCRIBE, ''.encode())

    def getStatus(self, id):
        assets = self.socket.recv_pyobj()

        return (id, assets[id])

#TODO revisit send/receive flags and poller to make more robust (cmds must be ack'd)
class APICommandReqCommunication:
    def __init__(self, uri="tcp://localhost:8889"):
        self.__setupZMQ(uri)

    def __setupZMQ(self, uri):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(uri)

    def sendCommand(self, cmd):
        self.socket.send_pyobj(cmd, flags=zmq.NOBLOCK)
        try:
            ack_message = self.socket.recv_pyobj()
            return ack_message
        except zmq.ZMQError:
            return None
