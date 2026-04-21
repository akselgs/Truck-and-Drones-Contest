#PLAN:
# 1-reinsert
# Choose random node:
#
# 4 scenarios:
# 
# 1- From truck to truck:
# Drones indexing are unchanged
#
# 2- From truck to drone:
# Verify truck is longer than drone
# Drone that is received by moved truck-node should follow the successor
# Drone that is sendt by moved truck-node should follow the predecessor
# These are always valid as we can not move depot nodes.
#
# Find all insertion options. by searching gaps in sendt and received indexing:
# Choose random insertion option, select random send and receive nodes within that window.
#
# 3- From drone to truck:
# New truck route follows the sending node to the drone-node and then to sending node's successor.
# 
# 4- From drone to drone: 
# Drone indexing are unchanged *or swapped between drones in case drone swap..
from SolutionRunner import SolutionRunner
import random
from collections import Counter
from itertools import pairwise
from itertools import groupby
import copy
from Common import copy_solution


def destroy_random_node_delete(runner, solution):
    #Cheaper to copy each part of the solution than a deepcopy.
    candidate = solution.copy()
    candidate["part1"] = solution["part1"][:]
    candidate["part2"] = solution["part2"][:]
    candidate["part3"] = solution["part3"][:]
    candidate["part4"] = solution["part4"][:]


    # -3 to exclude the zeroes in truck route and the divider in the drone route
    n_customers = len(candidate["part1"]) + len(candidate["part2"]) - 3 
    
    
    deletion = random.randint(1, n_customers)
    # print("Delete node:", deletion)
    unassigned = []
    
    if deletion in candidate["part1"]:
        index = candidate["part1"].index(deletion)
        candidate["part1"].remove(deletion)
        unassigned.append(deletion)

        if index in candidate["part3"]:
            index_indexing = candidate["part3"].index(index)
            candidate["part3"].remove(index)
            delete_drone = candidate["part2"][index_indexing]
            candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part4"].pop(index_indexing)
        
        if index in candidate["part4"]:
            index_indexing = candidate["part4"].index(index)
            candidate["part4"].remove(index)
            delete_drone = candidate["part2"][index_indexing]
            candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part3"].pop(index_indexing)
            
        candidate["part3"] = [x-1 if x >= index else x for x in candidate["part3"]]
        candidate["part4"] = [x-1 if x > index else x for x in candidate["part4"]]

    else:
        index = solution["part2"].index(deletion)
        candidate["part2"].remove(deletion)
        unassigned.append(deletion)
        candidate["part3"].pop(index)
        candidate["part4"].pop(index)

    return candidate, unassigned




def find_insert_positions(candidate):
    ###Format for insert positions is a dictionary of lists.
    ###For truck the list is simply indexes where we can insert the node
    ###For drones our dictionaries will contain a list of tuples:
    ###we create tuples for each sub-section where the drone is eligible for sending and receiving.
    #EXAMPLE
    # d1 is sent at index 0, received at index 3, sent at index 6. That means that the drone is eligible for sending and receiving in the gap 3-6, so the tuple will be (3,6).
    # This will result in the following search:
    # For sender 3 - receivers 4,5,6.
    # For sender 4 - receivers 5,6.
    # For sender 5 - receivers 6.
    # A simplification is to only consider 3,4,5 and 6 to target node, and the lowest two will consitute the best candidates for sending and receiving. 
    # This is not perfect however, as this can be non-feasible due to delaying another drone while one of the other combinations that we omit testing could fit.
    # To circumvent this we can check combinations of the best senders and receivers, but limit the maximum number of combination to check per subsection.
    # For small windows such as the example above (6 combinations), we can check all, but for larger windows we can limit this. 
    # We can also be greedy and search the best first- exiting once we find a fesible solution

    insert_positions = {
        "truck": [],
        "d1": [],
        "d2": [],
    }
    #TRUCK:
    #All 
    insert_positions["truck"] = list(range(1,len(candidate["part1"])))

    #DRONE:
    #We split list into two lists based on the delimiter -1.
    part3 = []
    current = []
    for x in candidate["part3"]:
        if x == -1:
            part3.append(current)
            current = []
        else:
            current.append(x)
    part3.append(current)

    part4 = []
    current = []
    for x in candidate["part4"]:
        if x == -1:
            part4.append(current)
            current = []
        else:
            current.append(x)
    part4.append(current)

    for i in range(2): #for each drone..
        #We make a "unavailable" and "available" list that indicate when the drones become available or unavaiable.
        #The drones are available at index 1 (1-indexed in calculate total arrival time..) and whenver a drone is received. (We copy the receivers list and add 0 at the start)
        #The drones are unavailable at index "end" and whenever a drone is sent. (We copy the senders list and add len(truck route) to the end)
        
        #We then make tuples for the spaces between available and unavailable and add those to our lists.
        available = part4[i]
        available.insert(0,1)
        
        unavailable = part3[i]
        unavailable.append(len(candidate["part1"]))

        for j in range(len(available)):
            if i == 0:
                insert_positions["d1"].append((available[j], unavailable[j]))
            else:
                insert_positions["d2"].append((available[j], unavailable[j]))
            
    #print("Insert positions:")
    #print(insert_positions)
    return insert_positions

#Deconstruct based on divider, and insert customer to part2, as well as correct indexes to part3 and part4.
def insert_to_drone(solution, node, sender, receiver, drone, divider_index):

    part2_1 = solution["part2"][:divider_index]
    part3_1 = solution["part3"][:divider_index]
    part4_1 = solution["part4"][:divider_index]

    part2_2 = solution["part2"][divider_index:]
    part3_2 = solution["part3"][divider_index:]
    part4_2 = solution["part4"][divider_index:]

    part2_2.pop(0)
    part3_2.pop(0)
    part4_2.pop(0)

    if drone == 0:
        part3_1.append(sender)
        part3_1.sort()
        index = part3_1.index(sender)

        part2_1.insert(index, node)
        part4_1.insert(index, receiver)
    
    if drone == 1:
        part3_2.append(sender)
        part3_2.sort()
        index = part3_2.index(sender)

        part2_2.insert(index, node)
        part4_2.insert(index, receiver)

    part2_1.extend([-1])
    part2_1.extend(part2_2)
    part3_1.extend([-1])
    part3_1.extend(part3_2)
    part4_1.extend([-1])
    part4_1.extend(part4_2)
    
    solution["part2"] = part2_1    
    solution["part3"] = part3_1
    solution["part4"] = part4_1

    return solution

def best_single_insert_random_select(runner, candidate, node):
    best_cost = float('inf')
    best_candidate_tuples = []
    best_truck_insertion = None
    #print("Candidate before insert")
    #print(candidate)
    insert_positions = find_insert_positions(candidate)

    #First we check truck insertions:
    for i in insert_positions["truck"]:
        test_candidate = copy_solution(candidate)

        test_candidate["part1"].insert(i,node)
        test_candidate["part3"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part3"]]
        test_candidate["part4"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part4"]]
        
        total, arr, dep, feas = runner.calculate_total_waiting_time(test_candidate)

        if feas and total < best_cost:

            #selected_candidate = copy_solution(test_candidate)
            best_truck_insertion = copy_solution(test_candidate)
            #best_candidates[0] = (total, selected_candidate)
            #best_candidates.sort(key=lambda x: x[0])
            best_cost = total.copy()
            valid_truck_insertion_found = True
    if best_truck_insertion:
        best_candidate_tuples.append((best_cost, best_truck_insertion))




    #Then we check drone insertions:
    divider_index = candidate["part2"].index(-1)
    for drone_index in range(2):
        if drone_index == 0:
            drone = "d1"
        else:
            drone = "d2"
        
        #Subsection contains a tuple for the drones' availability windows.
        for subsection in insert_positions[drone]:

            shortest_paths = []
            for truck_index in range(subsection[0], subsection[1]):
                #For this part we use truck_index -1 since we zero-index when refering to the drone-time matrix.
                path_length = runner.drone_times[node][candidate["part1"][truck_index-1]]
                #print("Path between node", node, "and node", candidate["part1"][truck_index-1], "is", path_length)
                #Keep the best 4. This can be tuned.
                if len(shortest_paths) < 4:
                    shortest_paths.append((path_length, truck_index))
                    shortest_paths.sort(key=lambda x: x[0])
                elif path_length < shortest_paths[-1][0]:
                    shortest_paths.pop()
                    shortest_paths.append((path_length, truck_index))
                    shortest_paths.sort(key=lambda x: x[0])

            #We create solutions for each subsection.
            #Solutions are searched best first, but "best" CAN break feasibility. If it doesn't and we find a feasible option, we exit early. we use found as a flag.
            found = False
            for (sender_path_length, sender_node_index) in shortest_paths:  
                for (receiver_path_length, receiver_node_index) in shortest_paths:
                    
                    if receiver_node_index > sender_node_index:
                        test_candidate = copy_solution(candidate)
                        test_candidate = insert_to_drone(test_candidate, node, sender_node_index, receiver_node_index, drone_index, divider_index)
                        total, arr, dep, feas = runner.calculate_total_waiting_time(test_candidate)
                        
                        if feas:
                            if len(best_candidate_tuples) < 5:
                                selected_candidate = copy_solution(test_candidate)

                                best_candidate_tuples.append((total, selected_candidate))
                                best_candidate_tuples.sort(key=lambda x: x[0])
                                found = True
                                break

                            else:
                                if total <= best_candidate_tuples[-1][0]:
                                    best_candidate_tuples.pop()
                                    selected_candidate = copy_solution(test_candidate)

                                    best_candidate_tuples.append((total, selected_candidate))
                                    best_candidate_tuples.sort(key=lambda x: x[0])
                                    found = True
                                    break
                if found:
                    break
    
    return best_candidate_tuples

def random_select_candidate(candidates):
    rand_max = len(candidates)
    selected = random.randint(0,rand_max-1)
    return candidates[selected][1], candidates[selected][0]

def one_reinsert(runner, solution=None):
    if not solution:
        solution = runner.solution
    
    candidate, unassigned = destroy_random_node_delete(runner, solution) #Good
    for node in unassigned:
        #candidate = single_insert(runner, candidate, node)
        candidate_tuples = best_single_insert_random_select(runner, candidate, node)
        if len(candidate_tuples) == 0:
            return None, None
        else:
            candidate, objective = random_select_candidate(candidate_tuples)
            #candidate = weighted_select_candidate(candidates)

    return candidate, objective