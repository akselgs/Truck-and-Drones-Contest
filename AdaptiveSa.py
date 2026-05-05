from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution, load_best, save_to_file
from TruckSectionReinsert import truck_section_reinsert
from FlattenSection import flatten_section
from MultipleReinsert import x_destroy_regret_reinsert
from TruckSectionReinsertRegret import truck_section_reinsert_regret


#For this adaptive SA, I have had the problem that it is hard to evaluate the "performance" of operators that are meant to explore.
#Rewarding based on SA accept, improvements and new best, heavily favours exploitative operators.
#
#Instead I will focus on just evaluating an operators ability to improve - namely it's average delta_e.
#I will also keep track of the "gradient" of the search: i.e. how much the solution is improving the last x iterations.
#When gradient is high, I want to assign higher weight to exploiting operators. 
# As we reach local optima, gradient goes to zero: in which case I want to tend towards uniform weight of operators.
# SUMMARY:
# Instead of quantifying exploration, I default to exploration unless we find exploitation to be fruitful.

def adaptive_sa(runner, iterations, filename):
    # Save and/or Load from file:
    all_time_best_solution = load_best(filename)
    if all_time_best_solution:
        all_time_best_objective, _,_,_ = runner.calculate_total_waiting_time(all_time_best_solution)
    else:
        all_time_best_objective = float('inf')
    this_run_best_objective = float('inf')


    # Calibration split:
    schedule_split = iterations // 100

    # How often prints for progress are displayed
    progress_split = 1000

    #How often we save our solution
    save_split = 1000
    
    #"Staleness" before we promote more exploratory operators:
    staleness_limit = iterations // 100

    delta_w = []
    t_f = 0.1

    ###Weights of operator. Should match nr of operators
    weights = [1.0, 1.0, 1.0, 1.0, 1.0]
    avg_delta_e = [0 ,0 ,0 ,0 ,0]
    decay = 0.01

    # We create a list of objectives, so we can keep track of how the gradient has improved the last X operators
    basin_obj = []
    obj_curr = 0
    gradient = 0



    #--Start
    result = runner.run()

    #Initial check that initial solution is feasible
    if result["feasible"]:
        best_solution = copy_solution(runner.solution)
        best_objective = result["objective"]
        incumbent_solution = copy_solution(runner.solution)
        incumbent_objective = result["objective"]
    else:
        print("ERROR- Initial result is not feasible")
    


    ## ---- START -----
    #
    #
    print("=== Adaptive Simulated Annealing ===")
    print()
    print()
    print("Iterations: ", iterations, "| Cooling schedule split: ", schedule_split)
    print()
    print("Progress will be printed every", progress_split, "iterations")
    print("Progress will be saved every", save_split, "iterations")
    print()
    print("Best objective: ", all_time_best_objective)
    print("Initial objective: ", best_objective)
    print("-----------------------------------------")
    



    #-- Calibrate cooling schedule
    print()
    print("Cooling schedule:")
    for w in range(schedule_split):

        #Random number to pass SA-threshold
        rand = random.randint(0,100)
        rand = rand/100
        
        #Progress update
        if (w % 100 == 0):
            print()
            print("Tuning: Iteration", w)


        #Operation choice
        op = random.choices([0, 1, 2, 3, 4], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        elif op == 2:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)
        elif op == 3:
            candidate_solution, candidate_objective = x_destroy_regret_reinsert(runner, incumbent_solution)
        elif op == 4:
            candidate_solution, candidate_objective = truck_section_reinsert_regret(runner, incumbent_solution)


        # Check feasibility and delta_e
        candidate_feasible = runner.is_solution_feasible(candidate_solution)
        delta_e = candidate_objective - incumbent_objective

        #Update accordingly
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)

        elif candidate_feasible:
            if rand < 0.8: 
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
            delta_w.append(delta_e)


    #Now, we can update initial temperatures and cooling based on the tuning.
    if len(delta_w) == 0:
        print("Error, delta_W is empty, likely indicating too small sample size.")

    delta_avg = sum(delta_w)/len(delta_w)
    t_0 = (-1 * delta_avg)/(math.log(0.8))
    alpha = (t_f / t_0) ** (1/(iterations - schedule_split))
    t = t_0
    print()
    #print("Improvements during tuning: ", delta_w)
    print("Average improvement:", delta_avg)
    print(iterations, schedule_split)
    print("Alpha:", alpha)
    print("Initial temperature and final temperature:", t_0, t_f)
    print("------------------------------")
    
    # Main iteration loop:
    print()
    print("Main loop")
    max_gradient = 0
    relative_gradient = 0
    basin_obj.append(incumbent_objective)

    for i in range(schedule_split, iterations):
        rand = random.randint(0,100)
        rand = rand/100

        


        #Operation choice
        op = random.choices([0, 1, 2, 3, 4], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        elif op == 2:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)
        elif op == 3:
            candidate_solution, candidate_objective = x_destroy_regret_reinsert(runner, incumbent_solution)
        elif op == 4:
            candidate_solution, candidate_objective = truck_section_reinsert_regret(runner, incumbent_solution)    

        #If no insertions are found using one-reinsert, it will return none.
        if not candidate_solution:
            continue

        #Double check feasibility
        candidate_feasible = runner.is_solution_feasible(candidate_solution)
        delta_e = candidate_objective - incumbent_objective

        

        #We always accept negative delte_e so we set p to 1 in these cases (saves computation and prevents p from exploding) 
        if delta_e < 0:
            p = 1.0
        else:
            p = math.exp(-1*delta_e/t) 
        
        if candidate_feasible and (delta_e < 0):
            incumbent_solution = copy_solution(candidate_solution)
            incumbent_objective = candidate_objective
            
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
            
            
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                #Once a new solution is explored - we let the inherited basin be the new relative (boosted by the increase in objective)
                relative_gradient = basin_obj[-1] - (best_objective)
                relative_gradient = (incumbent_objective - best_objective)/100
                #Then we empty the saved solutions we used to determine the old gradient.
                basin_obj = []
                

        if len(basin_obj) < staleness_limit:
            basin_obj.insert(0,incumbent_objective)
        else:
            basin_obj.pop()
            basin_obj.insert(0,incumbent_objective)
        gradient = basin_obj[-1] - incumbent_objective


        t = alpha * t

        

        #Update avg delta e for the used operator.
        avg_delta_e[op] = ((1-decay) * avg_delta_e[op]) + (decay * delta_e)

        gradient_normalized = min(1, gradient / relative_gradient) if relative_gradient > 0 else 0

        #Update weights based on theire avg_delta_e and the gradient.
        weights = update_weights(avg_delta_e, gradient_normalized, len(weights), i)

        #Progress print
        # if ((i) % progress_split == 0):
        #     print()
        #     print()
        #     print()
        #     print("Iteration:", i , "| Best objective:", best_objective)
        #     print("Weights")
        #     print("Op 1- Weight" ,float(weights[0]), "| Average Delta E:", avg_delta_e[0])
        #     print("Op 2- Weight" ,float(weights[1]), "| Average Delta E:", avg_delta_e[1])
        #     print("Op 3- Weight" ,float(weights[2]), "| Average Delta E:", avg_delta_e[2])
        #     print("Op 4- Weight" ,float(weights[3]), "| Average Delta E:", avg_delta_e[3])
        #     print("Op 5- Weight" ,float(weights[4]), "| Average Delta E:", avg_delta_e[4])
        #     print("Gradient Normalized")
        #     print(gradient_normalized)
            
  
        if i % save_split == 0:
            save_to_file(filename, best_solution, best_objective, this_run_best_objective, all_time_best_objective)

    save_to_file(filename, best_solution, best_objective, this_run_best_objective, all_time_best_objective)
    return best_solution

def update_weights(avg_delta_e, gradient_normalized, n_operators, i):
    worst_op = max(avg_delta_e)
    norm_avg = [x-worst_op for x in avg_delta_e]
    neg_avg = [-x for x in norm_avg]
    #neg_avg = [x if (x>0) else 0 for x in neg_avg]
    
    #return "weights"
    total = sum(neg_avg)
    
    if total > 0:
        exploit_weights = [d / total for d in neg_avg]
    else:
        exploit_weights = [1 / n_operators] * n_operators  # uniform fallback before data

    max_exploit = 0.9
    min_weight = (1 - max_exploit) / (n_operators - 1)
    exploit_weights = [
        max_exploit if ew > max_exploit else max(ew, min_weight)
        for ew in exploit_weights
    ]
    # Renormalize
    total = sum(exploit_weights)
    exploit_weights = [ew / total for ew in exploit_weights]
    
    weights = [
        gradient_normalized * ew + (1 - gradient_normalized) * (1 / n_operators)
        for ew in exploit_weights
    ]
    
    return weights