import zmq
import time

class APICommandReqCommunication:
    def __init__(self, uri="tcp://localhost:8889"):
        self.__setupZMQ(uri)

    def __setupZMQ(self, uri):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(uri)

    def run(self):
        messages = ["Aap", "Noot", "Mies", "Boom"]

        time.sleep(1.0)

        print("Starting to send commands...")

        for msg in messages:
            print(f"Send: {msg}")
            self.socket.send_string(msg, flags=zmq.NOBLOCK)
            time.sleep(2.0)
            try:
                print(self.socket.recv_string(flags=zmq.NOBLOCK))
            except zmq.ZMQError:
                print("No reply received after 2 sec")

        print("Finished sending commands")

if __name__ == '__main__':
    req_client = APICommandReqCommunication()
    req_client.run()
