import random
from Common import copy_solution
import bisect
from OneReinsert import best_single_insert_random_select, random_select_candidate

def flatten_section(runner, solution):

    max_drones_flattened = ((len(solution["part2"])-1) // 3)

    nr_drones_flatten = random.randint(1,max_drones_flattened+1)
    drone_customers = solution["part2"].copy()
    drone_customers.remove(-1)
    if len(drone_customers) == 0:
        cost, arr, dep, feas = runner.calculate_total_waiting_time(solution)
        return solution, cost
    
    drones_to_flatten = random.sample(drone_customers , nr_drones_flatten)


    candidate = copy_solution(solution)

    for node in drones_to_flatten:
        index_pos = candidate["part2"].index(node)
        insert_pos = candidate["part3"][index_pos]

        candidate["part1"].insert(insert_pos, node)
        candidate["part2"].pop(index_pos)
        candidate["part3"] = [x+1 if (x > insert_pos and x != -1) else x for x in candidate["part3"]]
        candidate["part4"] = [x+1 if (x > insert_pos and x != -1) else x for x in candidate["part3"]]
        candidate["part3"].pop(index_pos)
        candidate["part4"].pop(index_pos)
    try:
        cost, arr, dep, feas = runner.calculate_total_waiting_time(candidate)
    except:
        print(candidate)

    if feas:
        return candidate, cost
    else:

        cost, arr, dep, feas = runner.calculate_total_waiting_time(solution)
        return solution, cost 

# runner = 4
# solution = {
#     "part1" : [0,1,2,0],
#     "part2" : [3,4,-1,5],
#     "part3" : [1,3,-1,3],
#     "part4" : [2,4,-1,4],
#     }

# candidate, cost = flatten_section(runner, solution)
# print(candidate)

