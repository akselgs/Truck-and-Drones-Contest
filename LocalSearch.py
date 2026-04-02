import copy
from OneReinsert import one_reinsert

def local_search(initial_runner, iterations):
    candidate_runner = copy.deepcopy(initial_runner)
    best_runner = copy.deepcopy(initial_runner)

    result = initial_runner.run()
    if result["feasible"]:
        best_solution = initial_runner.solution
        best_objective = result["objective"]
    else:
        print("ERROR- Initial result is not feasible")
    

    for i in range(iterations):
        if (i % 100 == 0):
            print()
            print("Iteration", i)

        candidate_runner.solution = copy.deepcopy(best_solution)

        candidate_solution = one_reinsert(candidate_runner)
        candidate_runner.solution = candidate_solution
        total, arr, dep, feas = candidate_runner.calculate_total_waiting_time(candidate_solution)

        if total < best_objective:
            candidate_result = candidate_runner.run()
            if candidate_result["feasible"] and candidate_result["objective"] < best_objective:
                best_solution = copy.deepcopy(candidate_solution)
                best_objective = copy.deepcopy(candidate_result["objective"])
                print()
                print("NEW BEST:")
                print(best_solution)
                print(best_objective)

    best_runner.solution = best_solution

    return best_runner