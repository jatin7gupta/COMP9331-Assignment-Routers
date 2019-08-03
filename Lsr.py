import sys
import socket as s
import time
import threading
import pdb
import pickle
from collections import defaultdict, deque
from math import inf
import datetime as dt
from typing import Dict, List, Any, Union
import copy

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
        self.previous_sent_messages_sequence = defaultdict(int)
        self.global_routers_timestamp = defaultdict(float)
        self.global_routers = defaultdict(list)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
        self.global_routers[self.name].append(neighbour)

    def set_message(self, message):
        self.message = message

    def add_previous_sent_sequence(self, message):
        self.previous_sent_messages_sequence[message.name] = message.sequence_number

    def check_previous_sent_sequence(self, message):
        return self.previous_sent_messages_sequence[message.name] != message.sequence_number

    def add_router_timestamp(self, message):
        self.global_routers_timestamp[message.name] = message.timestamp

    def check_router_timestamp(self, message):
        return self.global_routers_timestamp[message.name] != message.timestamp

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

    def check_if_neighbour_alive(self, message):
        for neighbour in message.neighbours:
            if neighbour.name == self.name:
                present = False
                for my_neighbour in self.neighbours:
                    if my_neighbour.name == neighbour.name:
                        present = True
                if not present:
                    self.add_neighbour(neighbour)


class Message:
    def __init__(self, sender: Router):
        self.port = sender.port
        self.name = sender.name
        self.neighbours = sender.neighbours
        self.sequence_number = 0
        self.timestamp = dt.datetime.now().timestamp()
        self.last_sender = sender.name

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
    while True:
        time.sleep(ROUTER_UPDATE_INTERVAL)
        calculate_paths()


def calculate_paths():
    _parent_router = parent_router

    weight = 0
    visited_status = 1
    parent_ = 2

    g = Graph(_parent_router.global_routers)

    calculation_table: Dict[Any, List[Union[float, bool]]] = {}
    # (name, weight, visited=boolean)
    total_routers = 0
    for router in _parent_router.global_routers:
        if router != _parent_router.name:
            # filling all the table with name of router
            calculation_table[router] = [inf, False, None]
        else:
            calculation_table[router] = [0.0, True, None]
        total_routers += 1

    counter = 0
    print(f'I am Router {_parent_router.name}')
    current_router = _parent_router.name
    printing_routers = _parent_router.name
    printing_list = []
    while counter != total_routers-1:
        # code for opening up weights
        for edge in g.graph[current_router]:
            for node, weight_status in calculation_table.items():
                if node == edge.end and not weight_status[visited_status] and calculation_table[node][weight] > calculation_table[current_router][weight] + float(edge.weight):
                    calculation_table[node][weight] = calculation_table[current_router][weight] + float(edge.weight)
                    calculation_table[node][parent_] = edge.start
        min_weight = inf
        min_node = ''
        for node, weight_status in calculation_table.items():
            if weight_status[weight] < min_weight and weight_status[visited_status] == False:
                min_node = node
                min_weight = weight_status[weight]
        if min_node != '':
            calculation_table[min_node][visited_status] = True
            current_router = min_node
            counter += 1
            printing_list.append(min_node)
            printing_routers = printing_routers + min_node
    for node in printing_list:
        hops = node
        current_parent = calculation_table[node][parent_]
        while current_parent is not None:
            hops = hops + current_parent
            current_parent = calculation_table[current_parent][parent_]
        # TODO change this before submission
        # print(f'{_parent_router.name}->Least cost path to router {node}:{hops[::-1]} and the cost is {calculation_table[node][weight]:.1f}')
        print(f'Least cost path to router {node}:{hops[::-1]} and the cost is {calculation_table[node][weight]:.1f}')
    # print(calculation_table)


def udp_client(_parent_router: Router):
    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    while True:
        for child in _parent_router.neighbours:
            _parent_router.message.timestamp = dt.datetime.now().timestamp()
            message_to_send = pickle.dumps(_parent_router.message)
            server_port = int(child.port)
            client_socket.sendto(message_to_send, (SERVER_NAME, server_port))
        time.sleep(UPDATE_INTERVAL)
        _parent_router.message.increment_sequence_number()


def check_previous_sent_sequence(message: Message, _parent_router: Router):
    return _parent_router.previous_sent_messages_sequence[message.name] < message.sequence_number


def check_previous_sent_timestamp(message: Message, _parent_router: Router):
    return _parent_router.global_routers_timestamp[message.name] < message.timestamp


def forward_message(_parent_router, received_message):
    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    last_sender = received_message.last_sender
    for neighbour in _parent_router.neighbours:
        # dont send to the previous sender
        if last_sender != neighbour.name and check_previous_sent_timestamp(received_message, _parent_router):
            received_message.last_sender = _parent_router.name
            client_socket.sendto(pickle.dumps(received_message), (SERVER_NAME, int(neighbour.port)))
    _parent_router.add_previous_sent_sequence(received_message)
    _parent_router.add_router_timestamp(received_message)
    _parent_router.update_global_routers(received_message)
    client_socket.close()


def udp_server(_parent_router: Router):
    server_port = int(_parent_router.port)
    server_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
    server_socket.bind((SERVER_NAME, server_port))
    client_socket = s.socket(s.AF_INET, s.SOCK_DGRAM)

    while True:
        message, client_address = server_socket.recvfrom(2048)
        received_message: Message = pickle.loads(message, fix_imports=True, encoding="utf-8", errors="strict")

        # forward_message(_parent_router, received_message)
        last_sender = copy.deepcopy(received_message.last_sender)
        for neighbour in _parent_router.neighbours:
            # dont send to the previous sender
            if last_sender != neighbour.name and check_previous_sent_timestamp(received_message, _parent_router):
                received_message.last_sender = copy.deepcopy(_parent_router.name)
                client_socket.sendto(pickle.dumps(received_message), (SERVER_NAME, int(neighbour.port)))
        _parent_router.add_previous_sent_sequence(received_message)
        _parent_router.add_router_timestamp(received_message)
        _parent_router.check_if_neighbour_alive(received_message)
        _parent_router.update_global_routers(received_message)


def check_if_neighbours_alive(_parent_router: Router):
    neighbours_to_remove = None
    for neighbour in _parent_router.neighbours:
        if dt.datetime.now().timestamp() - _parent_router.global_routers_timestamp[neighbour.name] > 3:
            # print(f'I am {_parent_router.name} my neighbour {neighbour.name} is dead')
            # remove from LSA
            neighbours_to_remove = neighbour.name

            # remove from global key
            # remove from global values
    if neighbours_to_remove is not None:
        _parent_router.global_routers.pop(neighbours_to_remove, None)
        for neighbour in _parent_router.neighbours:
            if neighbours_to_remove == neighbour.name:
                _parent_router.neighbours.remove(neighbour)
                # print(f"I am {_parent_router.name}, my new neighbours are ")
                # for i in _parent_router.neighbours:
                #     print(i.name)
                # print('')
                break


def not_my_neighbour(router, _parent_router):
    for neighbour in _parent_router.neighbours:
        if router == neighbour.name:
            return False
    return True


def check_if_non_neighbours_alive(_parent_router: Router):
    router_to_remove = None
    for router, all_neighbours in _parent_router.global_routers.items():
        if not_my_neighbour(router, _parent_router) and router != _parent_router.name:
            if dt.datetime.now().timestamp() - _parent_router.global_routers_timestamp[router] > 12:
                # print(f'I am {_parent_router.name} -> {router} is dead')
                router_to_remove = router
    if router_to_remove is not None:
        _parent_router.global_routers.pop(router_to_remove, None)


def check_alive(_parent_router: Router):
    while True:
        time.sleep(3)
        check_if_neighbours_alive(_parent_router)
        check_if_non_neighbours_alive(_parent_router)


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
    check_alive_thread = threading.Thread(target=check_alive, args=(parent_router,))
    client_thread.start()
    server_thread.start()
    calculation_thread.start()
    check_alive_thread.start()
