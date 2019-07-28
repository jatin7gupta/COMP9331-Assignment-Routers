import sys
import socket as s
import time
import threading
import pdb
import pickle
from collections import defaultdict, deque
from math import inf

ARGS_NUMBER = 2
FILE_NAME = 1
ROUTER_NAME = 0
PARENT_PORT = 1
CHILD_PORT = 2
DISTANCE = 1
UPDATE_INTERVAL = 1
ROUTER_UPDATE_INTERVAL = 30
SERVER_NAME = 'localhost'


class Router:
    def __init__(self, name, port, neighbours_list):
        self.name = name
        self.port = port
        self.neighbours = neighbours_list
        self.message = None
        self.previous_sent_messages = set()
        self.global_routers = defaultdict(list)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
        self.global_routers[self.name].append(neighbour)

    def set_message(self, message):
        self.message = message

    def add_previous_sent(self, message):
        m = (message.port, message.sequence_number)
        self.previous_sent_messages.add(m)

    def check_previous_sent(self, message):
        m = (message.port, message.sequence_number)
        return m not in self.previous_sent_messages

    def update_global_routers(self, message):
        if len(self.global_routers[message.name]) > 0:
            for neighbour in message.neighbours:
                present = False
                for present_neighbour in self.global_routers[message.name]:
                    if present_neighbour.port == neighbour.port \
                            and present_neighbour.name == neighbour.name \
                            and present_neighbour.distance == neighbour.distance:
                        present = True
                if not present:
                    self.global_routers[message.name].append(neighbour)
        else:
            for neighbour in message.neighbours:
                self.global_routers[message.name].append(neighbour)


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


class Edge:
    def __init__(self, u, v, weight):
        self.start = u
        self.end = v
        self.weight = weight


class Graph:
    def __init__(self, global_routers):
        self.global_routers = global_routers
        self.graph = defaultdict(list)
        self.parse(self.global_routers)

    def parse(self, global_routers):
        for router, neighbours in global_routers.items():
            parent = router
            for child in neighbours:
                self.graph[parent].append(Edge(parent, child.name, child.distance))


def calculate_paths_activator():
    time.sleep(ROUTER_UPDATE_INTERVAL)
    calculate_paths()


def calculate_paths():
    _parent_router = parent_router

    weight = 0
    visited_status = 1

    g = Graph(_parent_router.global_routers)

    calculation_table = {}
    # (name, weight, visited=boolean)
    total_routers = 0
    for router in _parent_router.global_routers:
        if router != _parent_router.name:
            # filling all the table with name of router
            calculation_table[router] = [inf, False]
        else:
            calculation_table[router] = [0.0, True]
        total_routers += 1

    counter = 0
    while counter != total_routers-1:
        # code for opening up weights
        current_router = _parent_router.name
        for edge in g.graph[current_router]:
            for node, weight_status in calculation_table.items():
                if node == edge.end and not weight_status[visited_status] and calculation_table[node][weight] > calculation_table[current_router][weight] + float(edge.weight):
                    calculation_table[node][weight] = calculation_table[current_router][weight] + float(edge.weight)

        min_weight = inf
        min_node = ''
        for node, weight_status in calculation_table.items():
            if weight_status[weight] < min_weight and weight_status[visited_status] == False:
                min_node = node
                min_weight = weight_status[weight]

        calculation_table[min_node][visited_status] = True
        current_router = min_node
        counter += 1
    print(calculation_table)


def udp_client(_parent_router: Router):
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
        time.sleep(UPDATE_INTERVAL)
        _parent_router.message.increment_sequence_number()


def udp_server(_parent_router: Router):
    server_port = int(_parent_router.port)
    server_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    # server_socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_NAME, server_port))
    while True:
        message, client_address = server_socket.recvfrom(2048)
        received_message: Message = pickle.loads(message, fix_imports=True, encoding="utf-8", errors="strict")

        client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        for child in _parent_router.neighbours:
            if _parent_router.check_previous_sent(received_message):
                if child.port != received_message.port:
                    client_socket.sendto(pickle.dumps(received_message),
                                         (SERVER_NAME, int(child.port)))
                    _parent_router.add_previous_sent(received_message)

        _parent_router.update_global_routers(received_message)

        # for i in received_message.neighbours:
        #     print(received_message.name,'    --' ,i.name, i.port, received_message.sequence_number)


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

    parent_router.set_message(Message(parent_router))
    # TODO make them daemon
    client_thread = threading.Thread(target=udp_client, args=(parent_router,))
    server_thread = threading.Thread(target=udp_server, args=(parent_router,))
    calculation_thread = threading.Thread(target=calculate_paths_activator)
    client_thread.start()
    server_thread.start()
    calculation_thread.start()



