## Input: runner, and solution and node:
## Output: solution and score

import random
from Common import copy_solution
import bisect
from OneReinsert import best_single_insert_random_select, random_select_candidate

def truck_section_reinsert(runner, solution):
    max_section_length = len(solution["part1"])//3
    print("Max selection length:")
    print(max_section_length)
    section_length = random.randint(1,max_section_length+1)
    
    remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, shift, depot_sorties = delete_truck_section(runner, solution, section_length)
    best_candidate, best_cost = best_section_insert(remove_section, leftover_section, interior_nodes,exterior_nodes, orphans, shift, runner, solution, section_length, depot_sorties)


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
    # candidate["part1"] = [0,2,4,5,6,8,0]
    # candidate["part2"] = [3,7,-1,1]
    # candidate["part3"] = [1,4,-1,2]
    # candidate["part4"] = [3,7,-1,3]
    section_length = 3
    print()
    print("DESTROY")
    print("------------------")
    print("Selected section length")
    print(section_length)

    print(len(candidate["part1"]))
    if len(candidate["part1"]) in candidate["part4"]:
        pos = candidate["part4"].index(len(candidate["part1"]))
        sep = candidate["part4"].index(-1)
        if pos < sep:
            d = 0
        else:
            d = 1
    shifted_truck = candidate["part1"][0:-1]
    print("open truck path:")
    print(shifted_truck)

    shift = random.randint(0,len(shifted_truck)-1)
    shift = 1
    print("random_shift")
    print(shift)

    shifted_truck = shifted_truck[shift:] + shifted_truck[:shift]
    remove_section = shifted_truck[:section_length]
    
    print("shifted truck path")
    print(shifted_truck)
    print("Section to remove")
    print(remove_section)
    print("leftover truck route")
    leftover_section = shifted_truck[section_length:]
    print(leftover_section)

    
    interior_nodes = []
    orphans = []
    exterior_nodes = []
    depot_sorties = []

    drone_index = 0
    for i, node in enumerate(candidate["part2"]):
        if node == -1:
            drone_index += 1
            continue
        print("p1")
        print(candidate["part1"])
        print("p3")
        print(candidate["part3"])
        print("p4")
        print(candidate["part4"])
        print("sender index")
        print(candidate["part3"][i])
        print("receiver index")
        print(candidate["part4"][i])
        sender_node = candidate["part1"][candidate["part3"][i]-1]
        receiver_node = candidate["part1"][candidate["part4"][i]-1]
        if receiver_node == 0:
            print("Drone is received by depot and requires extra logic.")
            print("sender node")
            print(sender_node)
            print("receiver node")
            print(receiver_node)
            depot_sorties.append((node, sender_node, receiver_node, drone_index))
            continue
        print("sender node")
        print(sender_node)
        print("receiver node")
        print(receiver_node)

        if (sender_node in remove_section) and (receiver_node in remove_section):
            interior_nodes.append((node, sender_node, receiver_node, drone_index))
        elif (sender_node in remove_section) or (receiver_node in remove_section):
            orphans.append(node)
        else:
            exterior_nodes.append((node, sender_node, receiver_node, drone_index))

    return(remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, shift, depot_sorties)


def best_section_insert(remove_section, leftover_section, interior_nodes, exterior_nodes, orphans, shift, runner, solution, section_length, depot_sorties):

    print()
    print("Repair")
    print("------------------")
    candidate = leftover_section.copy()
    insert = remove_section.copy()

    best_candidate = copy_solution(solution)
    best_cost, arr, dep, feas = runner.calculate_total_waiting_time(solution)

    #For insertion positions
    for i in range(len(leftover_section)):
        #For orientation
        for o in range(2):
            truck_candidate = leftover_section.copy()
            insert = remove_section.copy()
            if o == 0:
                truck_candidate = leftover_section[:i] + insert + leftover_section[i:]
            else:
                insert.reverse()
                truck_candidate = leftover_section[:i] + insert + leftover_section[i:]

            shift = truck_candidate.index(0)
            truck_candidate = truck_candidate[shift:] + truck_candidate[:shift]
            truck_candidate.append(0)

            print("Candidate after adding back 0 and shifting back")
            print(truck_candidate)
            p2d1, p3d1, p4d1 = [], [], []
            p2d2, p3d2, p4d2 = [], [], []
            print("interior nodes")
            print(interior_nodes)
            print("exterior nodes")
            print(exterior_nodes)
            print("depot sorties")
            print(depot_sorties)
            print("orphans")
            print(orphans)
            for n, s, r, d in (interior_nodes + exterior_nodes):
                print("interior node")
                print("node, sender, receiver, drone")
                print(n,s,r,d)
                s_index = truck_candidate.index(s)
                r_index = truck_candidate.index(r)
                if d == 0:
                    if o == 0:
                        pos = bisect.bisect_left(p3d1, s_index)
                        p2d1.insert(pos,n)
                        p3d1.insert(pos,s_index+1)
                        p4d1.insert(pos,r_index+1)
                    else:
                        pos = bisect.bisect_left(p3d1, s_index)
                        p2d1.insert(pos,n)
                        p3d1.insert(pos,r_index+1)
                        p4d1.insert(pos,s_index+1)
                else:
                    if o == 0:
                        pos = bisect.bisect_left(p3d2, s_index)
                        p2d2.insert(pos,n)
                        p3d2.insert(pos,s_index+1)
                        p4d2.insert(pos,r_index+1)
                    else:
                        pos = bisect.bisect_left(p3d2, s_index)
                        p2d2.insert(pos,n)
                        p3d2.insert(pos,r_index+1)
                        p4d2.insert(pos,s_index+1)

            
            for n, s, r, d in (depot_sorties):
                s_index = truck_candidate.index(s)
                if d == 0:
                    pos = bisect.bisect_left(p3d1, s_index)
                    p2d1.insert(pos,n)
                    p3d1.insert(pos,s_index+1)
                    p4d1.insert(pos,len(truck_candidate))
                else:
                    pos = bisect.bisect_left(p3d1, s_index)
                    p2d1.insert(pos,n)
                    p3d1.insert(pos,s_index+1)
                    p4d1.insert(pos,len(truck_candidate))

            candidate = {
                "part1" : truck_candidate,
                "part2" : p2d1 + [-1] + p2d2,
                "part3" : p3d1 + [-1] + p3d2,
                "part4" : p4d1 + [-1] + p4d2,
            }
            print("---------")
            print("Candidate")
            print(candidate["part1"])
            print(candidate["part2"])
            print(candidate["part3"])
            print(candidate["part4"])

            print()

            
            obj, arr, dep, feas = runner.calculate_total_waiting_time(candidate)
            print("Results:")
            print(obj)
            print(feas)

            if feas:
                if len(orphans) > 0:
                    candidate_tuples = best_single_insert_random_select(runner, candidate, orphans)
                    if len(candidate_tuples) == 0:
                        return None, None
                    else:
                        candidate, objective = random_select_candidate(candidate_tuples)
                        #candidate = weighted_select_candidate(candidates)
                else:
                    objective = obj
                    if objective < best_cost:
                        print("New best found")
                        best_cost = objective
                        best_candidate = candidate

                        print("Best Candidate:")
                        print(candidate)
                        print("Cost")
                        print(objective)

    print("Best Candidate:")
    print(best_candidate)
    print("Cost")
    print(best_cost)




    return best_candidate, best_cost




