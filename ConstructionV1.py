from main import read_data, SolutionRunner, parse_solution
from itertools import pairwise
import math
import copy
import bisect

#filename = "Truck_Drone_Contest.txt"
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
        truck_route: list,
        drone_1: list,
        drone_2: list,
        drone_1_send: list,
        drone_2_send: list,
        drone_1_receive: list,
        drone_2_receive: list
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

#Traverse only by the truck.
def simple_traverse(nodes):
    travel_time = 0
    #print("---")
    #print("traversal: traversing", nodes)
    for from_node, to_node in pairwise(nodes):
        #print("from ", from_node, "to " , to_node, ": " ,truck_times[from_node][to_node])
        travel_time += truck_times[from_node][to_node]
    #print("travel time: ", travel_time)
    #print("---")
    return travel_time

def make_string(solution):
    product_string = ""
    for nodes in solution.truck_route:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "|"

    for nodes in solution.drone_1:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "-1,"

    for nodes in solution.drone_2:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "|"

    for i in solution.drone_1_send:
        product_string = product_string + str(i) + ","
    product_string = product_string + "-1,"

    for i in solution.drone_2_send:
        product_string = product_string + str(i) + ","
    product_string = product_string + "|"


    for i in solution.drone_1_receive:
        product_string = product_string + str(i) + ","
    product_string = product_string + "-1,"

    for i in solution.drone_2_receive:
        product_string = product_string + str(i) + ","

    return product_string

def make_runner(solution):
    construction_string = make_string(solution)
    construction_solution = parse_solution(construction_string)
    runner = SolutionRunner(
        solution=construction_solution,
        truck_times=truck_times,
        flight_time_matrix=drone_times,
        flight_range_limit=flight_range,
        depot_index=depot_index,
        max_iterations=10,
        convergence_threshold=1.0,
        n_drones=n_drones,
    )
    return runner

#Initialize
served_customers = [0, 0]
nodes_list = initialize(n_nodes)


#Main loop for truck only:
max_iterations = 100
iterations = 0
truck_times_copy = truck_times.copy()
truck_times_copy[: , 0]= -1
current_node = 0
while iterations < max_iterations:
    #Find the node that is furthest away from our path.
    next_candidate = truck_times_copy[current_node].argmax()
    truck_times_copy[: , next_candidate]= -1 #Set value negative so it is excluded from next iteration.

    #Now that we have our candidate, we want to insert it in our path. We check pairwise for the best position.
    best_candidate = math.inf
    for i in range(1,len(served_customers)):
        #We make a temporary copy that we can modify and insert the candidate
        temp_copy_served_customers = served_customers.copy()
        temp_copy_served_customers.insert(i, int(next_candidate))

        candidate_path_length = simple_traverse(temp_copy_served_customers)
        #print("candidate for list:", temp_copy_served_customers, ": " , candidate)

        #If better, we update our "best candidate" and its corresponding index
        if candidate_path_length < best_candidate:
            best_index = i
            best_candidate = candidate_path_length
        
    #print("best position is:",best_index)
    served_customers.insert(best_index, int(next_candidate))
    current_node = served_customers[-2]
    #print("list is now:", served_customers)
    #print("=============")
    #print(traverse(served_customers))

    iterations +=1

solution = Solution(
    truck_route= served_customers,
    drone_1 = [],
    drone_2 = [],
    drone_1_send = [],
    drone_2_send = [],
    drone_1_receive = [],
    drone_2_receive = []
)


runner = make_runner(solution)

print("Finished truck route:")
baseline_result = runner.run()
print("Baseline result", baseline_result["objective"])
print("====")
print("starting looking for drone candidates:")
#Try and find drone candidates


#Greedy sender approach.
#Traversing the truck route, each node has the option to send out a drone. Greedy because we select the best option for each sender which is determined by the initial truck route.
#There will be three loops to this process:
#Loop 1: This is the outermost loop and this loop increments the sender node. Loop 2 and 3 are therefore performed for each sender candidate.
#Loop 2: We substitute one node that has will be served by truck, so that it is instead served by drone. All nodes that will be served by truck are candidates (for node 1 there are 100 candidates, 2 have 99 candidates, ...)
#Loop 3: We check receive-nodes. We can limit this to the nodes in the truck path that does not superseed the flight time, as those would be non-feasible anyways.
#For each sender (loop 1) we pick the best solution from loop 2 and 3 as our new path. If there is no improvement (and therefore no change) we continue from next sender node.
#If there is an improvement (and a new path), we continue from the node where the drone is received.

#This is performed twice, once for each drone.


def greedy_sender(start_index, solution, drone_number):
    baseline_runner = make_runner(solution)
    baseline_result = baseline_runner.run()
    next_node_to_check = start_index+1
    best_solution = solution.copy()
    best_runner = make_runner(best_solution)
    best_result = best_runner.run()
    #loop 1:
    if start_index >= len(solution.truck_route):
        print("finished for drone:", drone_number)
        print(solution.truck_route)
        return (solution)
    print("====")
    print("Current starting node to explore, is node", solution.truck_route[start_index], "at index", start_index)
    print("Objective to beat:", baseline_result["objective"])
    #Start point should now be sender by index.

    #Candidates to be served by truck is all nodes that are "scheduled" to be served by truck.
    candidate_nodes = solution.truck_route[start_index+1:-1]
    print(len(candidate_nodes), "nodes can be potentially be served by drone from this starting point")
    #print("These candidate nodes are:" , candidate_nodes)
    print("----")

    #Receive candidates requires us to traverse the truck route to find nodes that does not superseed travel time.
    receive_candidates_endindex = start_index
    receive_candidates_length = 0
    i = 1
    while receive_candidates_length < flight_range:
        if start_index+i < len(solution.truck_route):
            receive_candidates_length = simple_traverse(solution.truck_route[start_index:receive_candidates_endindex])
            if receive_candidates_length < flight_range:
                receive_candidates_endindex = start_index + i
                i += 1
            else:
                print("nodes from ", start_index+1, "to", receive_candidates_endindex, "can be receival points")
                break
        else:
            print("all remaining nodes are candidates")
            break

    print("The next",  receive_candidates_endindex-start_index, "nodes are possible candidates. The length of this sub-path is ", receive_candidates_length)
    print("----")

    
    #Loop 2.
    for node in candidate_nodes:
        #We only want to overwrite when we find a new solution, and so we create a working copy.
        solution_copy = solution.copy()

        solution_copy.truck_route.remove(node)
        if drone_number == 1:
            solution_copy.drone_1.append(node)
            solution_copy.drone_1_send.append(start_index)
        elif drone_number == 2:
            solution_copy.drone_2.append(node)
            solution_copy.drone_2_send.append(start_index)
        
        #Loop 3:
        for receive_node in range(start_index+1, receive_candidates_endindex):
            if drone_number == 1:
                solution_copy.drone_1_receive = solution.drone_1_receive.copy() 
                solution_copy.drone_1_receive.append(receive_node)
            elif drone_number == 2:
                solution_copy.drone_2_receive = solution.drone_2_receive.copy()
                solution_copy.drone_2_receive.append(receive_node)
                cutoff = bisect.bisect_right(solution_copy.drone_1_send, receive_node)
                for i in range(cutoff, len(solution_copy.drone_1_send)):
                    solution_copy.drone_1_send[i] -=1
                cutoff = bisect.bisect_right(solution_copy.drone_1_receive, receive_node)
                for i in range(cutoff, len(solution_copy.drone_1_receive)):
                    solution_copy.drone_1_receive[i] -= 1

            runner = make_runner(solution_copy)
            stringer = make_string(solution_copy)
            
            #print("runner string is:", runner_string)
            result = runner.run()
            if (result["feasible"]):
                print("----")
                print("This candidate:", stringer)
                print("Objective: ", result["objective"])
                if result["objective"] < best_result["objective"]:
                    best_solution = solution_copy.copy()
                    best_result = result
                    next_node_to_check=receive_node
                    print("New best solution found!")
                    runner_string = make_string(solution_copy.copy())
                    print("New solution is: ", runner_string)
                    print("Objective: ", best_result["objective"], "- Feasibility: ", best_result["feasible"])
                    print("----")



    print("solution before node was checked: ", baseline_result["objective"], ": Feasibility: ", baseline_result["feasible"])
    print("solution after node was checked: ", best_result["objective"], ": Feasibility: ", best_result["feasible"])
    solution = best_solution

    
    return greedy_sender(next_node_to_check, best_solution, drone_number)


best_string = make_string(solution)


solution_1_drone = greedy_sender(0, solution, 1)

solution_2_drone = greedy_sender(0,solution_1_drone, 2)

best_string = make_string(solution_2_drone)

print("best string is ", best_string)
    
    
best_solution = parse_solution(best_string)

final_runner = SolutionRunner(
    solution=best_solution,
    truck_times=truck_times,
    flight_time_matrix=drone_times,
    flight_range_limit=flight_range,
    depot_index=depot_index,
    max_iterations=10,
    convergence_threshold=1.0,
    n_drones=n_drones,
)
final_result = final_runner.run()

print("Final result: Objective- ", final_result["objective"], "| Feasibility- ", final_result["feasible"])


    




    
    





#print(truck_times)