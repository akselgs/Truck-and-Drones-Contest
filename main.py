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
from AdaptiveSa import adaptive_sa
from pyinstrument import Profiler
from CreateInitSolution import create_initial_solution 

from concurrent.futures import ProcessPoolExecutor


filename = "Data/F_20.txt"
# ---------------------------------------------------------------------------
def run_for_file(filename):
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




    # ----------------------

    # --Initialization--
    # --
    runner = create_initial_runner(filename)


    initial_result = runner.run()

    new_solution = create_initial_solution(runner)
    print(new_solution)
    total, _, _, _ = runner.calculate_total_waiting_time(new_solution)

    runner.solution = new_solution
    print("=========")
    print()
    print(filename)
    print()
    print("===============")
    print("Initial runner objective")
    print(total)
    # ----------------------

    # --Transformation--
    # --

    start = time.time() 
    #new_solution = local_search(runner, 10000)
    #new_solution = sim_ann(runner, 10000)
    #new_solution = sim_ann_multiple_ops(runner, 10000)
    new_solution = adaptive_sa(runner, 10000, filename)


    # -- Results --
    # --
    if profile:
        profiler.stop()
        profiler.print()
        
        profiler.open_in_browser()



    end = time.time()
    print("Time taken:", filename)
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

    return((new_runner.solution, new_result["objective"]))





if __name__ == "__main__":
    filenames = [        
    "Data/R_10.txt",
    "Data/F_10.txt",
    "Data/R_20.txt",
    "Data/F_20.txt",
    "Data/R_50.txt",
    "Data/F_50.txt",
    "Data/R_100.txt",
    "Data/F_100.txt",
    ]
    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(run_for_file, filenames))