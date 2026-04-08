## Input: runner, and solution and node:
## Output: solution and score

import random
from Common import copy_solution

def truck_section_reinsert(runner, solution):

    max_section_length = len(solution["part1"])//4
    print("Max selection length:")
    print(max_section_length)
    section_length = random.randint(1,max_section_length)

    truck_section, destroyed_candidate, unassigned = delete_truck_section(runner, solution, section_length)
    return solution

def delete_truck_section(runner, solution, section_length):
    candidate = copy_solution(solution)
    truck_path_with_open_loop = candidate["part1"][0:-1]
    print("open truck path:")
    print(truck_path_with_open_loop)

    delete_node_index = random.randint(1, len(solution)-1)
    delete_node = candidate["part1"][delete_node_index]

    print("delete node")
    print(delete_node)
    print("delete node index")
    print(delete_node_index)

    print("lower end")
    print(delete_node_index-section_length)
    print("higher end")
    print(delete_node_index+section_length)
    truck_section = truck_path_with_open_loop[(delete_node_index-section_length):(delete_node_index+section_length)]
    print(truck_section)
    leftover_section = truck_path_with_open_loop[delete_node_index+section_length:delete_node_index-section_length]

    print(truck_section)
    print(leftover_section)
    unassigned = []

    return truck_section, leftover_section, unassigned

    




