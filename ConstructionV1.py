from main import read_data, SolutionRunner, parse_solution
from itertools import pairwise
import math

filename = "Truck_Drone_Contest.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(filename)
depot_index = 0
def initialize(n_nodes):
    #Generate list of nodes we can iterate through and potentially "exhaust"

    nodes_list = list(range(n_nodes+1))

    nodes_list.pop(0)#Generate list of customers we have served.
    

    return nodes_list

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

def make_string(served_by_truck, served_by_drone_1, served_by_drone_2, send_1, send_2, return_1, return_2):
    product_string = ""
    for nodes in served_by_truck:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "|"

    for nodes in served_by_drone_1:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "-1"

    for nodes in served_by_drone_2:
        product_string = product_string + str(nodes) + ","
    product_string = product_string + "|"

    for i in send_1:
        product_string = product_string + str(i) + ","
    product_string = product_string + "-1"

    for i in send_2:
        product_string = product_string + str(i) + ","
    product_string = product_string + "|"


    for i in return_1:
        product_string = product_string + str(i) + ","
    product_string = product_string + "-1"

    for i in return_2:
        product_string = product_string + str(i) + ","

    return product_string

def make_runner(served_by_truck, served_by_drone_1, served_by_drone_2, send_1, send_2, return_1, return_2):
    construction_string = make_string(served_by_truck, served_by_drone_1, served_by_drone_2, send_1, send_2, return_1, return_2)
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

served_by_truck = served_customers
served_by_drone_1 = []
served_by_drone_2 = []
send_1 = []
send_2 = []
return_1 = []
return_2 = []

runner = make_runner(served_by_truck, served_by_drone_1, served_by_drone_2, send_1, send_2, return_1, return_2)

print("Finished truck route:")
baseline_result = runner.run()
print("Baseline result", baseline_result["objective"])
print("====")
print("starting looking for drone candidates:")
#Try and find drone candidates

#Initialize baseline for best
best_runner = baseline_result
best_served_by_truck = served_by_truck
available_drones = 2
best_served_by_drone_1 = []
best_served_by_drone_2 = []
best_send_1 = []
best_send_2 = []
best_return_1 = []
best_return_2 = []
best_string = ""


#For each node we test if we can send drones from our node to speed up the process.
for enquiry_index in range(1, len(served_customers)-1):
#for i in range(0, 3):
    old_result = best_runner
    best_send_point = -1
    best_return_point = -1

    

    print("Enquiring node ", served_customers[enquiry_index], "at position ", enquiry_index)

    served_by_truck_copy = best_served_by_truck.copy()
    served_by_drone_1_copy = best_served_by_drone_1.copy()
    served_by_drone_2_copy = best_served_by_drone_2.copy()

    served_by_truck_copy.remove(served_customers[enquiry_index])


    print("truck is now serving" , len(served_by_truck), "customers")

    best_candidate = math.inf 
    for from_node in range(   max(0,enquiry_index-10)           ,    min(enquiry_index,len(served_customers)-1)):
        #Check for changes in drone availability
        if from_node in return_1:
            available_drones += 1
        if from_node in return_2:
            available_drones += 1
        if from_node in send_1:
            available_drones -= 1
        if from_node in send_2:
            available_drones -= 1

        if available_drones not in (0, 1, 2):
            print("an error has happened with drones- available:", available_drones)

        if available_drones == 0:
            continue

        for to_node in range( max(enquiry_index,from_node+1)   ,    min(enquiry_index+10,len(served_customers))):
            served_by_drone_1_copy = best_served_by_drone_1.copy()
            served_by_drone_2_copy = best_served_by_drone_2.copy()
            send_1_copy = best_send_1.copy()
            return_1_copy = best_return_1.copy()
            send_2_copy = best_send_2.copy()
            return_2_copy = best_return_2.copy()

            if available_drones == 2:
                served_by_drone_1_copy.append(served_customers[enquiry_index])
                
                send_1_copy.append(from_node)
                return_1_copy.append(to_node)
            elif available_drones == 1:
                served_by_drone_2_copy.append(served_customers[enquiry_index])
                
                send_2_copy.append(from_node)
                return_2_copy.append(to_node)

            runner_string = make_string(served_by_truck_copy, served_by_drone_1_copy, served_by_drone_2_copy, send_1_copy, send_2_copy, return_1_copy, return_2_copy)
            runner_candidate = make_runner(served_by_truck_copy, served_by_drone_1_copy, served_by_drone_2_copy, send_1_copy, send_2_copy, return_1_copy, return_2_copy)
            print("attempting solution for", runner_string)
            runner_result = runner_candidate.run()
            if runner_result["feasible"]:
                if runner_result["objective"] < best_runner["objective"]:
                    best_runner = runner_result
                    best_string = runner_string
                    best_served_by_truck = served_by_truck_copy
                    best_served_by_drone_1 = served_by_drone_1_copy
                    best_served_by_drone_2 = served_by_drone_2_copy
                    best_send_1 = send_1_copy
                    best_return_1 = return_1_copy
                    best_send_2 = send_2_copy
                    best_return_2 = send_2_copy
                    best_send_point = from_node
                    best_return_point = to_node

                    print("New best:", best_runner["objective"])

    
    
    print("best position for node", served_customers[enquiry_index], ": start at " , best_send_point, "end at ", best_return_point )
    print("Previous result: ", old_result["objective"], "New result", best_runner["objective"])
    #served_by_truck = best_served_by_truck
    # served_by_drones = 
    # send_index = best_send_index
    # return_index = best_return_index

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
final_runner.run()


    




    
    





#print(truck_times)