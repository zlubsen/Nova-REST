import zmq
import time

def loop(sub_socket):
    #print("API looping")

    try:
        status_data = sub_socket.recv_pyobj(flags=zmq.NOBLOCK)
        print(f"We received: {status_data}")
    except zmq.ZMQError:
        #print("Nothing here...")
        pass


def main():
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)

    sub_socket.connect("tcp://localhost:5556")
    sub_socket.setsockopt(zmq.SUBSCRIBE, ''.encode())

    while True:
        loop(sub_socket)

    sub_socket.close()
    context.term()

if __name__ == '__main__':
    main()
