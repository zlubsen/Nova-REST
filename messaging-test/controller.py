import zmq
import time
from random import randrange

pub_frequency = 500
last_pub_time = int(round(time.time() * 1000))

def pumpStatus(pub_socket):
    status_data = [randrange(180),
                randrange(180),
                randrange(180),
                randrange(180),
                randrange(180),
                randrange(255)]

    print("Pumping status")
    pub_socket.send_pyobj(status_data)

def loop(pub_socket):
    global last_pub_time

    #print("Controller looping {}".format(time.time()))
    # send out status updates
    current_time = int(round(time.time() * 1000))
    time_diff =  current_time - last_pub_time
    if time_diff > pub_frequency:
        pumpStatus(pub_socket)
        last_pub_time = current_time

def main():
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5556")

    while True:
        loop(pub_socket)

    pub_socket.close()
    context.term()

if __name__ == '__main__':
    main()
