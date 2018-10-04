import zmq
from collections import deque

class APICommandRepCommunication:
    def __init__(self, uri="tcp://*:8889"):
        self.__setupZMQ(uri)
        self.receivedCommands = deque()

    def __setupZMQ(self, uri):
        self.context = zmq.Context()
        self.server = self.context.socket(zmq.REP)
        self.server.bind(uri)

        self.poller = zmq.Poller()
        self.poller.register(self.server, zmq.POLLIN)

    def __listenForCommand(self):
        api_cmd = None
        socks = dict(self.poller.poll(200))
        if socks.get(self.server) == zmq.POLLIN:
            api_cmd = self.server.recv_string()
            self.server.send_string(f"Ack {api_cmd}", flags=zmq.NOBLOCK)

        return api_cmd

    def readCommand(self):
        return self.receivedCommands.popleft()

    def run(self, cmds):
        api_cmd = self.__listenForCommand()
        print(f"Received: {api_cmd}")

        #if not api_cmd == None:
        #    self.receivedCommands.append(api_cmd)

    def cleanup(self):
        self.server.close()
        self.context.term()
        self.poller.unregister()

if __name__ == '__main__':
    rep_server = APICommandRepCommunication()
    while True:
        rep_server.run([])
