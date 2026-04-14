## Input: runner, and solution and node:
## Output: solution and score

import random
from Common import copy_solution

def truck_section_reinsert(runner, solution):

    max_section_length = len(solution["part1"])//3
    print("Max selection length:")
    print(max_section_length)
    section_length = random.randint(1,max_section_length+1)
    print("Selected section length")
    print(section_length)
    truck_section, destroyed_candidate, unassigned = delete_truck_section(runner, solution, section_length)
    return solution

def delete_truck_section(runner, solution, section_length):
    candidate = copy_solution(solution)
    # Remove ending 0
    truck_path_with_open_loop = candidate["part1"][0:-1]
    print("open truck path:")
    print(truck_path_with_open_loop)

    random_shift = random.randint(0,len(truck_path_with_open_loop))
    print("random_shift")
    print(random_shift)

    remove_section = truck_path_with_open_loop[random_shift:] + truck_path_with_open_loop[:random_shift]
    remove_section = remove_section[:section_length]
    print("shifted truck path")
    print(remove_section)
    print("leftover truck route") = remove_section[section_length:]


    interior_nodes = []
    orphans = []
    exterior_nodes = []

    drone_id = 0
    for i, node in enumerate(candidate["part2"]):
        if node == -1:
            drone_index += 1
            continue

        launch_node = candidate["part1"][candidate["part3"][i]]
        receiver_node = candidate["part1"][candidate["part4"][i]]

        if (launch_node in remove_section) and (receiver_node in remove_section):
            interior_nodes.append(node)
        elif (launch_node in remove_section) or (receiver_node in remove_section):
            orphans.append(node)
        else:
            exterior_nodes.append(node)




