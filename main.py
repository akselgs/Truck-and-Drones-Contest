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
from pyinstrument import Profiler




# ---------------------------------------------------------------------------

### ---START--- ###
profile = False
if profile:
    profiler = Profiler()
    profiler.start()
# --
# --
# --Fixed Parameters--
n_drones = 2 #fixed
drone_capacity = 1 #fixed
depot_index=0 #fixed
# --------------------

# --File selection--
# --
filename = "Data/F_100.txt"

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




# -- Results --
# --
if profile:
    profiler.stop()
    profiler.print()
    
    profiler.open_in_browser()

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


