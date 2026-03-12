from InitialSolution import create_initial_runner
from RandomSolution import create_random_runner
import time

filename = "Truck_Drone_Contest_new.txt"
#filename = "Data/F_10.txt"
#filename = "Data/F_20.txt"
#filename = "Data/F_50.txt"
#filename = "Data/F_100.txt"
#filename = "Data/R_10.txt"
filename = "Data/R_20.txt"
#filename = "Data/R_50.txt"
#filename = "Data/R_100.txt"


### BLIND RANDOM SEARCH:
#
def blind_random_search(filename):
    initial_runner = create_initial_runner(filename)
    initial_result = initial_runner.run()
    best_runner = initial_runner
    best_objective = initial_result["objective"]
    print(best_objective)

    start = time.time()
    iterations = 10000

    for i in range(iterations):
        current_runner = create_random_runner(filename)
        current_result= current_runner.run()

        if current_result["feasible"]:
            current_objective = current_result["objective"]
            #print("feasible solution found")
            #print(current_objective)
            if current_objective < best_objective:
                best_objective = current_objective
                best_runner = current_runner
                print("New best!")
                print(best_objective)

        if (i%1000 == 0):
            print("iteration", i)

    end = time.time()
    print("=================")
    total_time = end-start
    print("Time taken: ", total_time)
    print("Time per random search: ", total_time/iterations)
    print("Best objective: ", best_objective)
    return best_objective, total_time, initial_result["objective"], best_runner

objectives = []
times = []

for i in range(1):
    obj, tot_time, init_obj, best_runner = blind_random_search(filename)
    objectives.append(obj)
    times.append(tot_time)

best_obj = min(objectives)
print()
print("===========")
print("Average objective: ", sum(objectives)/len(objectives))
print("Best objective: ", best_obj)
print("Initial objective: ", init_obj)
print("Improvement: ", 100 * (init_obj - best_obj)/init_obj, "%")
print("Average time: ", sum(times)/len(times))
print()
print("Objectives: ")
print(objectives)
print()
print("Times")
print(times)
print("Solution:")
print(best_runner.solution)
