import zmq

class StatusPublishSubCommunication:
    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)

        socket.connect("tcp://localhost:8888")
        socket.setsockopt(zmq.SUBSCRIBE, ''.encode())

    def getStatus(id):
        assets = socket.recv_pyobj()

        return (id, assets[id])


#poller = zmq.Poller()
#poller.register(socket, zmq.POLLIN)

#socks = dict(poller.poll(500))
#if socks.get(socket) == zmq.POLLIN:
#message = socket.recv()
