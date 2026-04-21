## Input: runner, and solution and node:
## Output: solution and score

import random
from Common import copy_solution
import bisect
from OneReinsert import best_single_insert_random_select, random_select_candidate

def truck_section_reinsert(runner, solution):

    max_section_length = len(solution["part1"])//3
    section_length = random.randint(1,max_section_length+1)
    
    remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, depot_sorties = delete_truck_section(runner, solution, section_length)
    best_candidate, best_cost = best_section_insert(remove_section, leftover_section, interior_nodes,exterior_nodes, orphans, runner, solution, depot_sorties)


    return best_candidate, best_cost

### Returns truck section, leftover section, external nodes, internal nodes, orphaned nodes and shift
#Removes a section of the truck and returns the removed section and the broken leftover solution
#The leftover is also shifted, and may also not contain the depot node.
#To repair, we need to insert the removed section into our solution, then shift the route in order to align 0 to the start and append 0 to the end (returns shift).
#Then finally we need to reassign drones, there are 3 types:
#Internal nodes are completely contained within the removed section
#External nodes are completely outside the removed section
#Orphaned nodes are assigned using the repair function from earlier from 1-reinsert. Max 4 nodes will need to be assigned this way.

def delete_truck_section(runner, solution, section_length):
    candidate = copy_solution(solution)


    if len(candidate["part1"]) in candidate["part4"]:
        pos = candidate["part4"].index(len(candidate["part1"]))
        sep = candidate["part4"].index(-1)
        if pos < sep:
            d = 0
        else:
            d = 1
    shifted_truck = candidate["part1"][0:-1]

    shift = random.randint(0,len(shifted_truck)-1)
    shift = 1

    shifted_truck = shifted_truck[shift:] + shifted_truck[:shift]
    remove_section = shifted_truck[:section_length]

    leftover_section = shifted_truck[section_length:]

    
    interior_nodes = []
    orphans = []
    exterior_nodes = []
    depot_sorties = []

    drone_index = 0
    for i, node in enumerate(candidate["part2"]):
        if node == -1:
            drone_index += 1
            continue
        sender_node = candidate["part1"][candidate["part3"][i]-1]
        receiver_node = candidate["part1"][candidate["part4"][i]-1]

        if receiver_node == 0:
            depot_sorties.append((node, sender_node, receiver_node, drone_index))
            continue

        if (sender_node in remove_section) and (receiver_node in remove_section):
            interior_nodes.append((node, sender_node, receiver_node, drone_index))
        elif (sender_node in remove_section) or (receiver_node in remove_section):
            orphans.append(node)
        else:
            exterior_nodes.append((node, sender_node, receiver_node, drone_index))

    return(remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, depot_sorties)


def best_section_insert(remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, runner, solution, depot_sorties):
    best_cost = float('inf')
    best_candidate = None

    #For insertion positions
    for i in range(len(leftover_section)+1):
        #For orientation
        for o in range(2):
            truck_candidate = leftover_section.copy()
            insert = remove_section.copy()
            if o == 1:
                insert.reverse()
            truck_candidate = leftover_section[:i] + insert + leftover_section[i:]

            # We shift back so 0 is at the start again, and add the 0 at the end back
            shift = truck_candidate.index(0)
            truck_candidate = truck_candidate[shift:] + truck_candidate[:shift]
            truck_candidate.append(0)

            p2d1, p3d1, p4d1 = [], [], []
            p2d2, p3d2, p4d2 = [], [], []

            exterior_nodes.sort(key=lambda x: truck_candidate.index(x[1]))
            if o == 0:
                interior_nodes.sort(key=lambda x: truck_candidate.index(x[1]))
            else:
                interior_nodes.sort(key=lambda x: truck_candidate.index(x[2]))

            all_nodes = sorted(
                exterior_nodes + 
                [(n, r, s, d) if o == 1 else (n, s, r, d) for n, s, r, d in interior_nodes] +
                [(n, s, 0, d) for n, s, r, d in depot_sorties if n not in orphans],
                key=lambda x: truck_candidate.index(x[1])
            )

            for n, s, r, d in all_nodes:
                s_index = truck_candidate.index(s)
                r_index = truck_candidate.index(r) if r != 0 else len(truck_candidate) - 1
                if d == 0:
                    p2d1.append(n)
                    p3d1.append(s_index + 1)
                    p4d1.append(r_index + 1)
                else:
                    p2d2.append(n)
                    p3d2.append(s_index + 1)
                    p4d2.append(r_index + 1)

            candidate = {
                "part1" : truck_candidate,
                "part2" : p2d1 + [-1] + p2d2,
                "part3" : p3d1 + [-1] + p3d2,
                "part4" : p4d1 + [-1] + p4d2,
            }

            # Very costly if we check orphans for all insert positions. Instead we select ideal insert position first, then add orphans later.
            obj, arr, dep, feas = runner.calculate_total_waiting_time(candidate)
            # We could improve performance here by only checking boundaries instead of the whole length.. but this is easier

            if (obj < best_cost) and feas:
                best_candidate = copy_solution(candidate)
                best_cost = obj.copy()

    if best_candidate:    
        if len(orphans) > 0:
            for node in orphans:
                candidate_tuples = best_single_insert_random_select(runner, best_candidate, node)
                
                if len(candidate_tuples) == 0:
                    return None, None
                else:
                    candidate, objective = random_select_candidate(candidate_tuples)
                if objective < best_cost:
                    best_candidate = candidate
                    best_cost = objective
    
    else:
        return None, None

    return best_candidate, best_cost




