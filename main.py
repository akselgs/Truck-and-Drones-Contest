from FeasibiltyCheck import SolutionFeasibility
from CalCulateTotalArrivalTime import CalCulateTotalArrivalTime
import numpy as np
from OneReinsert import one_reinsert
from SolutionRunner import SolutionRunner
from Common import parse_solution, read_data
from InitialSolution import create_initial_runner, create_new_runner
from LocalSearch import local_search
from SimAnn import sim_ann
import time
from SimAnnMultipleOps import sim_ann_multiple_ops


# ---------------------------------------------------------------------------

# LEFTOVERS:
# Construction example string for use with Truck_Drone_Contest_new:
# ("0,54,25,58,71,40,74,24,65,17,79,30,61,52,42,87,7,13,85,77,20,29,19,2,93,3,66,27,81,53,34,55,63,99,90,45,84,21,62,5,10,36,8,22,64,68,92,16,96,48,35,9,72,83,67,46,88,6,15,32,11,33,69,80,41,82,31,14,95,12,1,86,44,47,97,91,50,4,49,57,51,0,|98,43,23,38,100,60,78,39,18,89,75,70,59,94,56,28,26,73,-1,76,37,|1,5,13,15,20,25,32,34,38,42,44,47,53,59,64,70,72,76,-1,39,62,|5,13,15,20,25,32,34,38,42,44,47,53,58,64,70,72,76,81,-1,40,63,")


### ---START--- ###
# --
# --
# --Fixed Parameters--
n_drones = 2 #fixed
drone_capacity = 1 #fixed
depot_index=0 #fixed
# --------------------

# --File selection--
# --
filename = "Data/F_10.txt"

# ----------------------

# --Initialization--
# --
runner = create_initial_runner(filename)


initial_result = runner.run()


print("Initial runner solution")
print(runner.solution)
print("Initial runner objective:")
print(initial_result["objective"])
print("Feasibility:")
print(initial_result["feasible"])
# ----------------------

# --Transformation--
# --

start = time.time()
#new_solution = local_search(runner, 10000)
#new_solution = sim_ann(runner, 10000)
new_solution = sim_ann_multiple_ops(runner, 10000)
end = time.time()
print("Time taken:")
print()
print(end - start)
print()
new_runner = create_new_runner(filename, new_solution)
new_result = new_runner.run(debug=True)
print("new solution:")
print(new_runner.solution)
print("new_result:")
print()
print(new_result["objective"])
print()
print("feas", new_result["feasible"])


