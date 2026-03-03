from main import read_data, SolutionRunner, parse_solution
import random
from Solution import Solution
from itertools import pairwise

filename = "Truck_Drone_Contest_new.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)
depot_index = 0

def initialize(n_nodes):
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(1,n_nodes+1))
    nodes_list.pop()#Generate list of customers we have served.
    
    return nodes_list


nodes_list = initialize(n_nodes)
random.shuffle(nodes_list)

splitpoints = []
for i in range(2):
    splitpoints.append(random.randint(0,n_nodes))

splitpoints = sorted(splitpoints)
splitpoints = [splitpoints[0], splitpoints[1]-splitpoints[0], n_nodes-splitpoints[1]]
splitpoints = sorted(splitpoints)
print(splitpoints)

random_solution = Solution([0],[],[],[],[],[],[])
random_solution.truck_route.extend(nodes_list[:splitpoints[2]])
random_solution.truck_route.append(0)

random_solution.drone_1.extend(nodes_list[splitpoints[2]:splitpoints[2]+splitpoints[1]])

random_solution.drone_2.extend(nodes_list[splitpoints[2]+splitpoints[1]:])
print("Assigned to truck:")
print(random_solution.truck_route)
print("Assigned to drone 1:")
print(random_solution.drone_1)
print("Assigned to drone 2:")
print(random_solution.drone_2)

print("===")
print("Finding send points:")



random_solution.drone_1_send = random.sample(
        list(range(1,len(random_solution.truck_route))), len(random_solution.drone_1)
    )
random_solution.drone_1_send = sorted(random_solution.drone_1_send)

random_solution.drone_2_send = random.sample(
        list(range(1,len(random_solution.truck_route))), len(random_solution.drone_2)
    )
random_solution.drone_2_send = sorted(random_solution.drone_2_send)


for i,j in pairwise(random_solution.drone_1_send):
    return_point = random.randint(i+1,j)
    random_solution.drone_1_receive.append(return_point)
if len(random_solution.drone_1_send) != 0:
    random_solution.drone_1_receive.append(random.randint(random_solution.drone_1_send[-1]+1, len(random_solution.truck_route)))

for i,j in pairwise(random_solution.drone_2_send):
    return_point = random.randint(i+1,j)
    random_solution.drone_2_receive.append(return_point)
if len(random_solution.drone_2_send) != 0:
    random_solution.drone_2_receive.append(random.randint(random_solution.drone_2_send[-1]+1, len(random_solution.truck_route)))

print()
print(random_solution.to_solution_string())


print("====================")
print("Length of truck path:", len(random_solution.truck_route))
print("Length of drone 1: ", len(random_solution.drone_1), len(random_solution.drone_1_send), len(random_solution.drone_1_receive))
print("length of drone 2: ", len(random_solution.drone_2), len(random_solution.drone_2_send), len(random_solution.drone_2_receive))


solution = parse_solution(random_solution.to_solution_string())

runner = SolutionRunner(
    solution=solution,
    truck_times=truck_times,
    flight_time_matrix=drone_times,
    flight_range_limit=flight_range,
    depot_index=depot_index,
    max_iterations=10,
    convergence_threshold=1.0,
    n_drones=n_drones,
)

runner.run()