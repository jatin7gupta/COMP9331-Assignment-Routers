import sys
import pdb


class Router:

    def __init__(self, name, port, neighbours_list):
        self.name = name
        self.port = port
        self.neighbours = neighbours_list

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)


if len(sys.argv) == 2:
    f = open(sys.argv[1], "r")
    line_counter = 0
    number_of_neighbour = 0
    # pdb.set_trace()
    parent_router: Router
    list_file = []
    for line in f:
        list_file.append(line.split())
    for i in range(len(list_file)):
        if i == 0:
            parent_router = Router(list_file[i][0], list_file[i][1], [])
        elif i == 1:
            number_of_neighbour = list_file[i]
        elif i > 1:
            child_router = Router(list_file[i][0], list_file[i][2], [])
            parent_router.add_neighbour(child_router)
        line_counter += 1
    print(parent_router)
    for i in parent_router.neighbours:
        print(i.name)

