import copy
from main import read_data, SolutionRunner, parse_solution
import random

filename = "Truck_Drone_Contest_new.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)
depot_index = 0
def initialize(n_nodes):
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(n_nodes+1))

    nodes_list.pop(0)#Generate list of customers we have served.
    
    return nodes_list


class Solution():
    def __init__(
        self,
        truck_route: list = [],
        drone_1: list = [],
        drone_2: list = [],
        drone_1_send: list = [],
        drone_2_send: list = [],
        drone_1_receive: list = [],
        drone_2_receive: list = [],
    ):
        self.truck_route = truck_route
        self.drone_1 = drone_1
        self.drone_2 = drone_2
        self.drone_1_send = drone_1_send
        self.drone_2_send = drone_2_send
        self.drone_1_receive = drone_1_receive
        self.drone_2_receive = drone_2_receive
    
    def copy(self):
        return Solution(
            truck_route=copy.deepcopy(self.truck_route),
            drone_1=copy.deepcopy(self.drone_1),
            drone_2=copy.deepcopy(self.drone_2),
            drone_1_send=copy.deepcopy(self.drone_1_send),
            drone_2_send=copy.deepcopy(self.drone_2_send),
            drone_1_receive=copy.deepcopy(self.drone_1_receive),
            drone_2_receive=copy.deepcopy(self.drone_2_receive),
        )
    

nodes_list = initialize(n_nodes)
random.shuffle(nodes_list)

random_solution = Solution(truck_route = nodes_list)
active_1 = False
active_2 = False

while(len(nodes_list) != 0):
    current_node = nodes_list.pop()
    random_int = random.randint(1,4)

    match random_int:
        case 1: continue

        case 2:
            if not active_1:
                random_solution.truck_route.remove(current_node)
                random_solution.drone_1.append(current_node)
                random_solution.drone_1_send()
            else:
                random_solution.drone_1_receive()
        case 3:
            if not active_2:
                random_solution.truck_route.remove(current_node)
                random_solution.drone_2.append(current_node)
                random_solution.drone_2_send()
            else:
                random_solution.drone_2_receive()
        case 4:
            if active_1:
                continue
            if active_2:
                continue


    seed += 1
    nodes_list.pop()
