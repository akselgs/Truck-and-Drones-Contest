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

def destroy_random_delete(runner):
    print("Destroy : 1")
    n_nodes = len(runner.solution["part1"]) + len(runner.solution["part2"]) - 3
    deletion = random.randint(1,n_nodes)

    deletion = 3
    print("Delete node:", deletion)

    if deletion in runner.solution["part1"]:
    
        index = runner.solution["part1"].index(deletion)
        runner.solution["part1"].remove(deletion)
        while index in runner.solution["part3"]:
            index_indexing = runner.solution["part3"].index(index)
            runner.solution["part3"].remove(index)
            runner.solution["part2"].pop(index_indexing)
            runner.solution["part4"].pop(index_indexing)
        
        while index in runner.solution["part4"]:
            index_indexing = runner.solution["part4"].index(index)
            runner.solution["part4"].remove(index)
            runner.solution["part2"].pop(index_indexing)
            runner.solution["part3"].pop(index_indexing)
            
        runner.solution["part3"] = [x-1 if x >= index else x for x in runner.solution["part3"]]
        runner.solution["part4"] = [x-1 if x > index else x for x in runner.solution["part4"]]
    elif deletion in runner.solution["part2"]:
        index = runner.solution["part2"].index(deletion)
        runner.solution["part2"].remove(deletion)
        runner.solution["part3"].pop(index)
        runner.solution["part4"].pop(index)

    print()
    print(runner.solution)
    return runner


def fix_random_insert(runner):
    ok = True

    print("Does this happen??")
    try:
        runner.run()
        total_nodes = runner.feasibility
        print()
        print("Complete solution? ---", total_nodes.is_complete_solution(runner.solution))
        ok = False
    except:
        ok = False
        print("not OK")
        
    while not ok:
        ok = True
        print("Exited by cheating")
    return runner


#Random removal- random insert
def one_reinsert(runner):
    runner = destroy_random_delete(runner)
    runner = fix_random_insert(runner)
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

new_runner = destroy_random_delete(example_runner)
print("New runner:")
print(new_runner.solution)
new_runner_fixed = fix_random_insert(new_runner)
print(new_runner_fixed.run())