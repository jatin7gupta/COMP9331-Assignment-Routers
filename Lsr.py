import sys
import socket as s
import time
import threading
import pdb
import pickle
from collections import deque

ARGS_NUMBER = 2
FILE_NAME = 1
ROUTER_NAME = 0
PARENT_PORT = 1
CHILD_PORT = 2
DISTANCE = 1
UPDATE_INTERVAL = 4
SERVER_NAME = 'localhost'


class Router:
    def __init__(self, name, port, neighbours_list):
        self.name = name
        self.port = port
        self.neighbours = neighbours_list
        self.message = None
        self.queue = deque()
        self.previous_sent_messages = set()

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)

    def set_message(self, message):
        self.message = message

    def append_queue(self, message):
        self.queue.append(message)

    def deque_queue(self):
        ret_val = self.queue.popleft()
        return ret_val

    def add_previous_sent(self, message):
        m = (message.port, message.sequence_number)
        self.previous_sent_messages.add(m)

    def check_previous_sent(self, message):
        m = (message.port, message.sequence_number)
        return m not in self.previous_sent_messages


class Message:
    def __init__(self, sender: Router):
        self.port = sender.port
        self.name = sender.name
        self.neighbours = sender.neighbours
        self.sequence_number = 0

    def increment_sequence_number(self):
        self.sequence_number += 1


class Neighbours:
    def __init__(self, name, port, distance):
        self.name = name
        self.port = port
        self.distance = distance


def udp_client(_parent_router: Router):
    # this client will have 2 tasks
    # 1. send my message to the child DONE
    # 2. forward the message received, to my child by checking if I have not sent it previously

    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    # TODO
    # client_socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    # client_socket.bind((SERVER_NAME, int(_parent_router.port)))
    while True:
        for child in _parent_router.neighbours:
            message_to_send = pickle.dumps(_parent_router.message)
            server_port = int(child.port)
            client_socket.sendto(message_to_send, (SERVER_NAME, server_port))
            _parent_router.add_previous_sent(_parent_router.message)

            while len(_parent_router.queue) > 0:
                message_received_from_neighbour = _parent_router.deque_queue()
                if _parent_router.check_previous_sent(message_received_from_neighbour):
                    if child.port != message_received_from_neighbour.port:
                        client_socket.sendto(pickle.dumps(message_received_from_neighbour), (SERVER_NAME, server_port))
                        _parent_router.add_previous_sent(message_received_from_neighbour)

        time.sleep(UPDATE_INTERVAL)
        _parent_router.message.increment_sequence_number()


def udp_server(_parent_router: Router):
    server_port = int(_parent_router.port)
    server_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    server_socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_NAME, server_port))
    while True:
        message, client_address = server_socket.recvfrom(2048)
        received_message: Message = pickle.loads(message, fix_imports=True, encoding="utf-8", errors="strict")
        _parent_router.queue.append(received_message)



        for i in received_message.neighbours:
            print(received_message.name,'    --' ,i.name, i.port, received_message.sequence_number)



if len(sys.argv) == ARGS_NUMBER:
    f = open(sys.argv[FILE_NAME], "r")
    line_counter = 0
    number_of_neighbour = 0
    # pdb.set_trace()
    parent_router: Router
    list_file = []
    for line in f:
        list_file.append(line.split())
    for i in range(len(list_file)):
        # First line will always be Parent router
        if i == 0:
            parent_router = Router(list_file[i][ROUTER_NAME], list_file[i][PARENT_PORT], [])

        # Second line will always be the number of neighbours
        elif i == 1:
            number_of_neighbour = list_file[i]  # TODO not using right now

        # From 3 onwards it will be the child routers
        elif i > 1:
            child_router = Neighbours(list_file[i][ROUTER_NAME], list_file[i][CHILD_PORT], list_file[i][DISTANCE])
            parent_router.add_neighbour(child_router)
        line_counter += 1

    # parent_router.add_message(Message(parent_router))
    parent_router.set_message(Message(parent_router))
    client_thread = threading.Thread(target=udp_client, args=(parent_router,))
    server_thread = threading.Thread(target=udp_server, args=(parent_router,))
    client_thread.start()
    server_thread.start()



