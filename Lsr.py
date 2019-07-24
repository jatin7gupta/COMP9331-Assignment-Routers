import sys
import pdb

ARGS_NUMBER = 2
FILE_NAME = 1
ROUTER_NAME = 0
PARENT_PORT = 1
CHILD_PORT = 2
DISTANCE = 1


class Router:
    def __init__(self, name, port, neighbours_list):
        self.name = name
        self.port = port
        self.neighbours = neighbours_list

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)


class Neighbours:
    def __init__(self, name, port, distance):
        self.name = name
        self.port = port
        self.distance = distance


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

    for i in parent_router.neighbours:
        print('Parent name = ', parent_router.name, 'child name->', i.name)

