import sys
from socket import *
import time
import concurrent.futures
import pdb

ARGS_NUMBER = 2
FILE_NAME = 1
ROUTER_NAME = 0
PARENT_PORT = 1
CHILD_PORT = 2
DISTANCE = 1
UPDATE_INTERVAL = 1


class Router:
    def __init__(self, name, port, neighbours_list):
        self.name = name
        self.port = port
        self.neighbours = neighbours_list

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)


class Message:
    def __init__(self, sender: Router):
        self.port = sender.port
        self.name = sender.name
        self.neighbours = sender.neighbours


class Neighbours:
    def __init__(self, name, port, distance):
        self.name = name
        self.port = port
        self.distance = distance


def udp_client(_parent_router):
    while True:
        server_name = 'localhost'
        for child in _parent_router.neighbours:
            message_to_send = f'hello router {child.name} I am your parent {parent_router.name}'
            server_port = int(child.port)
            client_socket = socket(AF_INET, SOCK_DGRAM)
            client_socket.sendto(str.encode(message_to_send), (server_name, server_port))
            client_socket.close()
        time.sleep(UPDATE_INTERVAL)


def udp_server(_parent_router):
    server_port = int(_parent_router.port)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', server_port))
    while True:
        message, client_address = server_socket.recvfrom(2048)
        print(f'I am server {_parent_router.name}, I have recieved data= {message} from port {client_address}')


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

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(udp_client, parent_router)
        executor.submit(udp_server, parent_router)
        executor.shutdown()
    # udp_client(parent_router)
    #
    # udp_server()

    # client code


