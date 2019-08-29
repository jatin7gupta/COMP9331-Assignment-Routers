# COMP9331 Assignment
## Goal and learning objectives
For this assignment, your task is to implement the link state routing protocol. Your program will be
running at all routers in the specified network. At each router, the input to your program is a set of directly
attached routers (i.e. neighbours) and the costs of these links. Each router will broadcast link-state packets
to all other routers in the network. Your routing program at each router should report the least-cost path
and the associated cost to all other routers in the network. Your program should be able to deal with failed
routers.
## Learning Objectives
On completing this assignment, you will gain sufficient expertise in the following skills:
1. Designing a routing protocol
2. Link state (Dijkstra’s) algorithm
3. UDP socket programming
4. Handling routing dynamics
