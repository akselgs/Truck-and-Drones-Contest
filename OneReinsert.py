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


def destroy_random_delete(runner):
    candidate = copy.deepcopy(runner.solution)
    n_nodes = len(candidate["part1"]) + len(candidate["part2"]) - 3
    
    deletion = random.randint(1,n_nodes)
    # print("Delete node:", deletion)
    unassigned = []
    
    if deletion in candidate["part1"]:
    
        index = candidate["part1"].index(deletion)
        candidate["part1"].remove(deletion)
        unassigned.append(deletion)
        while index in candidate["part3"]:
            index_indexing = candidate["part3"].index(index)
            candidate["part3"].remove(index)
            delete_drone = candidate["part2"][index_indexing]
            candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part4"].pop(index_indexing)
        
        while index in candidate["part4"]:
            index_indexing = candidate["part4"].index(index)
            candidate["part4"].remove(index)
            delete_drone = candidate["part2"][index_indexing]
            candidate["part2"].pop(index_indexing)
            unassigned.append(delete_drone)
            candidate["part3"].pop(index_indexing)
            
        candidate["part3"] = [x-1 if x >= index else x for x in candidate["part3"]]
        candidate["part4"] = [x-1 if x > index else x for x in candidate["part4"]]
    elif deletion in runner.solution["part2"]:
        index = runner.solution["part2"].index(deletion)
        candidate["part2"].remove(deletion)
        unassigned.append(deletion)
        candidate["part3"].pop(index)
        candidate["part4"].pop(index)

    # print()
    # print("Succesful deletion! Candidate solution is now:")
    # print(candidate)
    # print("Unassigned nodes to be inserted:")
    # print(unassigned)
    return candidate, unassigned


def fix_semi_random_insert(candidate, unassigned, runner):
    # print("Trying to fix candidate")
    try:
        feasibility = runner.feasibility
        # print()
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
        # print("Diagnose")
        # print()
        # print("Start and stop ok? ---", start_stop)
        # print()
        # print("Consistent ok? ---", consistent)
        # print()
        # print("Complete ok? ---", complete)

        if not start_stop:
            runner = fix_start_stop(runner)
        if not consistent:
            runner = fix_consistent(runner)

        
        if not complete:
            for node in unassigned:
                candidate = single_insert(candidate, node, runner)
                if not candidate:
                    print("No new inserts found, returning old candidate instead")
                    return runner.solution
                # print(candidate)

                #TODO method for making runner from candidate
    return candidate


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
        #print()
        #print("Finding insert positions for drone", i+1)
        senders = part3[i]
        senders.append(len((candidate["part1"])))
        #print("senders:", senders)

        receivers = part4[i]
        receivers.insert(0,1)
        #print("receivers:", receivers)

        all_sending_points = []
        all_receiving_points = []

        for j in range(len(senders)):
            
            sending_point = list(range(receivers[j], senders[j]))
            #print("sending points in sub-section:", sending_point)
            receiving_point = list(range(receivers[j]+1, senders[j]+1))
            #print("receiving points in sub-section:", receiving_point)
            all_sending_points.append(sending_point)
            all_receiving_points.append(receiving_point)

        if i == 0:
            insert_positions["d1"] = [all_sending_points, all_receiving_points]
        elif i == 1:
            insert_positions["d2"] = [all_sending_points, all_receiving_points]
        else:
            print("ERROR!")
    # print()
    # print("Successfully found insert postitions:")
    # print(insert_positions)
    return insert_positions


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


def single_insert(candidate, node, runner):

    best_cost = float('inf')
    best_candidates = None
    # print()
    # print("Finding best insert for:")
    # print(candidate)

    total, arr, dep, feas = runner.calculate_total_waiting_time(candidate)

    # print("With baseline of:")
    # print(total)
    # print("Feasibility:")
    # print(feas)
    insert_positions = find_insert_positions(candidate, node)

    #Start with truck:
    for i in insert_positions["truck"]:
        test_candidate = copy.deepcopy(candidate)
        test_candidate["part1"].insert(i,node)
        test_candidate["part3"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part3"]]
        test_candidate["part4"] = [x+1 if (x >= i and x != -1) else x for x in candidate["part4"]]

        total, arr, dep, feas = runner.calculate_total_waiting_time(test_candidate)
        # print()
        # print("Candidate:")
        # print(test_candidate)
        # print("Travel time:")
        # print(total)
        # print("Feasibility: ", feas)

        if ((total <= best_cost) and (feas)):
            # print()
            # print("New best!")
            # print(test_candidate)
            # print(total)
            best_candidates = test_candidate
            best_cost = total

    # print()
    # print("Best candidate after checking truck!:")
    # print(best_candidates)
    # print("Total time:")
    # print(best_cost)

    #Then check drones:
    #d1 is a list of senders and receivers, d1[0] is a list of all senders subsections: d1[0][0] is a single subsection with sender candidates and d1[0][0][0] is an actual node_index. 4 loops..
    for drone_index in range(2):
        if drone_index == 0:
            drone = "d1"
        else:
            drone = "d2"
        
        for subsection_index in range(len(insert_positions[drone][0])):
            sender_subsection = insert_positions[drone][0][subsection_index]
            receiver_subsection = insert_positions[drone][1][subsection_index]
            for sender in sender_subsection:
                possible_receivers = [x for x in receiver_subsection if x>sender]
                for receiver in possible_receivers:
                    test_candidate = copy.deepcopy(candidate)
                    divider_index = test_candidate["part2"].index(-1)
                    test_candidate = insert_to_drone(test_candidate, node, sender, receiver, drone_index, divider_index)

                    total, arr, dep, feas = runner.calculate_total_waiting_time(test_candidate)
                    # print()
                    # print("Candidate:")
                    # print(test_candidate)
                    # print("Travel time:")
                    # print(total)
                    # print(feas)

                    if ((total <= best_cost) and (feas)):
                        # print()
                        # print("New best!")
                        # print(test_candidate)
                        # print(total)
                        best_candidates = test_candidate
                        best_cost = total

    # print()
    # print("Best candidate after checking drones: ")
    # print(best_candidates)
    # print("Total time:")
    # print(best_cost)
    # if not best_candidates:
    #     print("no new candidate found, returning old candidate")
    #     return candidate

    return best_candidates

def fix_consistent(runner):
    return runner


def one_reinsert(runner):
    candidate, unassigned = destroy_random_delete(runner)
    total, arr, dep, feas = runner.calculate_total_waiting_time(candidate)
    # print("Destroyed candidate:")
    # print(candidate)
    # print("Objective")
    # print(total)
    # print("Feasibility")
    # print(feas)

    new_candidate = fix_semi_random_insert(candidate, unassigned, runner)
    if not new_candidate:
        print("no new candidate found, returning old candidate")
        return candidate
    return new_candidate