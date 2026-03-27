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
# New truck route follows the sending node to the drone-node and then to sending node's sucessor.
# 
# 4- From drone to drone: 
# Drone indexing are unchanged *or swapped between drones in case drone swap..
from InitialSolution import create_initial_runner
from main import SolutionRunner, read_data, parse_solution
import random
from collections import Counter
from itertools import pairwise
from itertools import groupby
import copy


def destroy_random_delete(runner):
    print("Destroy : 1")
    candidate = copy.deepcopy(runner.solution)
    n_nodes = len(candidate["part1"]) + len(candidate["part2"]) - 3
    
    deletion = random.randint(1,n_nodes)
    deletion = 3 #############################################TODO remove this...
    print("Delete node:", deletion)
    unassigned = []
    
    if deletion in candidate["part1"]:
    
        index = candidate["part1"].index(deletion)
        candidate["part1"].remove(deletion)
        unassigned.append(deletion)
        while index in candidate["part3"]:
            index_indexing = candidate["part3"].index(index)
            candidate["part3"].remove(index)
            delete_drone = candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part4"].pop(index_indexing)
        
        while index in candidate["part4"]:
            index_indexing = candidate["part4"].index(index)
            candidate["part4"].remove(index)
            delete_drone = candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part3"].pop(index_indexing)
            
        candidate["part3"] = [x-1 if x >= index else x for x in candidate["part3"]]
        candidate["part4"] = [x-1 if x > index else x for x in candidate["part4"]]
    elif deletion in runner.solution["part2"]:
        index = runner.solution["part2"].index(deletion)
        candidate["part2"].remove(deletion)
        unassigned.append(delete_drone)
        candidate["part3"].pop(index)
        candidate["part4"].pop(index)

    print()
    print("Sucessful deletion! Candidate solution is now:")
    print(candidate)
    print("Unassigned nodes to be inserted:")
    print(unassigned)
    return candidate, unassigned


def fix_semi_random_insert(candidate, unassigned, runner):
    try:
        feasibility = runner.feasibility
        print()
        start_stop = feasibility.is_truck_route_feasible(candidate)
        complete = feasibility.is_complete_solution(candidate)
        consistent = feasibility.are_parts_consistent(candidate)
    except:
        ok = False
        print("Error was thrown when checking feasibility..")

    ok = start_stop and complete and consistent

    if ok:
        print("Candidate is already valid!")
        print("(This probably shouldn't happen)")
        return candidate

    else:
        print("Invalid candidate.")
        print()
        print("Start and stop ok? ---", start_stop)
        if not start_stop:
            runner = fix_start_stop(runner)


        print()
        print("Complete ok? ---", complete)
        if not complete:
            for node in unassigned:
                single_insert(candidate, node, runner)
                print(candidate)


        print()
        print("Consistent ok? ---", consistent)
        if not consistent:
            runner = fix_consistent(runner)


        ok = start_stop and complete and consistent
        print("OK? ---", ok)
        ok = True
    return runner


def fix_start_stop(runner):
    print("Start-Stop error. Not implemented this yet/Shouldn't happen")
    return runner

def find_insert_positions(candidate, node):
    insert_positions = {
        "truck": [],
        "d1": [[],[]],
        "d2": [[],[]],
    }
    #TRUCK:
    insert_positions["truck"] = list(range(1,len(candidate["part1"])))

    #Drone:
    part3 = [
        [] if k else list(group)
        for k, group in groupby(candidate["part3"], lambda x: x == -1)
    ]
    part4 = [
        [] if k else list(group)
        for k, group in groupby(candidate["part4"], lambda x: x == -1)
    ]
    #part4 = [list(group) for k, group in groupby(candidate["part4"], lambda x: x == -1) if not k]
    
    #[3,5,-1,5] -> [[3,5][5]] so i a list.
    for i in range(2):
        #print()
        #print("Finding insert positions for drone", i+1)

        senders = part3[i]
        senders.insert(0,0)
        #print("senders:", senders)

        receivers = part4[i]
        receivers.append(len(candidate["part1"]))
        #print("receivers:", receivers)

        all_sending_points = []
        all_receiving_points = []
        for j in range(len(senders)):
            sending_point = list(range(senders[j], receivers[j]-1))
            #print("sending points in sub-section:", sending_point)
            receiving_point = list(range(senders[j]+1, receivers[j]))
            #print("receiving points in sub-section:", receiving_point)
            all_sending_points.append(sending_point)
            all_receiving_points.append(receiving_point)

            if i == 0:
                insert_positions["d1"] = [all_sending_points, all_receiving_points]
            elif i == 1:
                insert_positions["d2"] = [all_sending_points, all_receiving_points]
            else:
                print("ERROR!")
    print()
    print("Successfully found insert postitions:")
    print(insert_positions)
    return insert_positions

def single_insert(candidate, node, runner):
    best_cost = float('inf')
    best_candidates = None

    insert_positions = find_insert_positions(candidate, node)

    #Start with truck:
    for i in insert_positions["truck"]:
        test_candidate = copy.deepcopy(candidate)
        test_candidate["part1"].insert(i,node)
        test_candidate["part3"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part3"]]
        test_candidate["part4"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part4"]]

        total, arr, dep, feas = runner.calculate_total_waiting_time(test_candidate)
        print()
        print(candidate)
        print("Candidate:")
        print(test_candidate)
        print("Travel time:")
        print(total)
        print(feas)

        if ((total <= best_cost) and (feas)):
            best_candidates = test_candidate
            best_cost = total

    print("Best candidate for truck found:")
    print(best_candidates)
    print("Total time:")
    print(best_cost)

    #d1 is a list of senders and receivers, d1[0] is a list of all senders subsections: d1[0][0] is a single subsection with sender candidates and d1[0][0][0] is an actual node_index.
    for drone_index in range(2):
        if drone_index == 0:
            for subsection_index in range(len(insert_positions["d1"][0])):
                sender_subsection = insert_positions["d1"][0][subsection_index]
                receiver_subsection = insert_positions["d1"][1][subsection_index]
                for sender in sender_subsection:
                    possible_receivers = [x for x in receiver_subsection if x>sender]
                    for receivers in possible_receivers:
                        
                    print("Sender and receivers:")
                    print(sender)
                    print(possible_receivers)
        elif drone_index == 1:
            print("e")

    return best_candidates

    # part1 = runner.solution.get("part1", [])
    # part2 = runner.solution.get("part2", [])
    # part3 = runner.solution.get("part3", [])
    # part4 = runner.solution.get("part4", [])
    
    # truck_customers = [c for c in part1 if c != 0]
    # drone_customers = [x for x in part2 if x != -1]

    # freq = Counter(truck_customers + drone_customers)
    # expected_customers = set(range(1, runner.feasibility.n_nodes))
    # unserved_customers = list((Counter(expected_customers) - freq).elements())
    # print("Unserved customers:", unserved_customers)

    # #Select random sending point.
    # #Find best return point (ties - break by first return)
    # #
    # runner_copy = runner.copy()
    # for customer in unserved_customers:
    #     print("trying to serve customer", customer)

    #     send_rec_candidates = find_send_rec_candidates(runner_copy)
    #     print()
    #     print("send rec candidates:", send_rec_candidates)
    #     drone_partition_index = part2.index(-1)+1
    #     print("drone partition index", drone_partition_index)

    #     #Prioritize adding nodes as drones. but random to not make it deterministic
    #     population = [True, False]
    #     weights = [1, 0]
    #     choice = random.choices(population, weights=weights, k=1)[0]

    #     if choice or (len(send_rec_candidates[0]) < drone_partition_index):
    #         print("Trying to add by drone")
    #         selected_partition = random.sample(range(0,len(send_rec_candidates[0])),1)[0]
    #         print("Selected partition:", selected_partition)

    #         sender = random.sample(send_rec_candidates[0][selected_partition],1)[0]
    #         print("selected sender_node:", sender)

    #         possible_receivers = [x for x in send_rec_candidates[1][selected_partition] if x>sender]
    #         print("possible_receivers:")
    #         print(possible_receivers)

    #         for receiver in possible_receivers:
    #             sub_path = part1[sender:receiver+1]
    #             truck_path_length = calculate_truck_path(runner.truck_times, sub_path)
    #             print("truck subpath:", truck_path_length)
    #             flight_path_length = calculate_flight_path(runner.flight_time_matrix, part1[sender], part1[receiver], customer)
    #             print("flight path:", flight_path_length)
    #             if flight_path_length < runner.flight_range_limit:
    #                 print("okk")
                    
    #     else:
    #         print("Trying to add by truck")
    
    # return runner

def fix_consistent(runner):
    return runner






example_filename = "Data/F_10.txt"
n_nodes, n_customers, n_drones, flight_range, truck_times, drone_times, flight_range, drone_capacity = read_data(example_filename)
depot_index = 0
example_runner = SolutionRunner(
    solution=parse_solution("0,5,3,2,6,9,4,7,0,|8,10,1,-1,|2,3,5,-1,|3,4,6,-1,"),
    truck_times=truck_times,
    flight_time_matrix=drone_times,
    flight_range_limit=flight_range,
    depot_index=depot_index,
    max_iterations=10,
    convergence_threshold=1.0,
    n_drones=n_drones,
)
print("Example runner:")
print(example_runner.solution)
print(example_runner.run())

candidate, unassigned = destroy_random_delete(example_runner)
new_runner_fixed = fix_semi_random_insert(candidate, unassigned, example_runner)
print(new_runner_fixed.run())