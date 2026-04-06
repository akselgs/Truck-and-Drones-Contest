import copy
from OneReinsert import one_reinsert
from Common import copy_solution
def local_search(runner, iterations):

    result = runner.run()
    if result["feasible"]:
        best_solution = copy_solution(runner.solution)
        best_objective = result["objective"]
        early_stop_counter = 0
    else:
        print("ERROR- Initial result is not feasible")
    

    for i in range(iterations):
        if (i % 100 == 0):
            print()
            print("Iteration", i)
            print("Early stop counter")
            print(early_stop_counter)
        early_stop_counter += 1
        if early_stop_counter > 10000:
            print("early_stop")
            return best_solution
        
        candidate_solution = copy_solution(best_solution)

        candidate_solution, candidate_objective = one_reinsert(runner, candidate_solution)
        if not candidate_solution:
            print("No new insertions were found, continuing to next iteration.")
            continue

        
        if (candidate_objective < best_objective) and (runner.is_solution_feasible(candidate_solution)):
            best_solution = copy_solution(candidate_solution)
            best_objective = candidate_objective
            early_stop_counter = 0

            print()
            print("NEW BEST:")
            print(best_solution)
            print(best_objective)

    return best_solution