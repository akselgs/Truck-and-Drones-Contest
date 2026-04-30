from OneReinsert import one_reinsert
import random
import math
from Common import copy_solution, load_best, save_to_file
from TruckSectionReinsert import truck_section_reinsert
from FlattenSection import flatten_section


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
    progress_split = 500

    #How often we save our solution
    save_split = 1000
    

    delta_w = []
    t_f = 0.1

    ###Weights of operator. Should match nr of operators
    weights = [1.0, 1.0, 1.0]
    min_p = 0.1
    weight_split = 10 * len(weights)
    counts = [0, 0 ,0]
    gradient = 0
    avg_delta_e = [0,0,0]
    decay = 0.1


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
    print("Weights will be updated every", weight_split, "iterations")
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
        op = random.choices([0, 1, 2], weights=weights)[0]
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)


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
    print("Improvements during tuning: ", delta_w)
    print("Average improvement:", delta_avg)
    print(iterations, schedule_split)
    print("Alpha:", alpha)
    print("Initial temperature and final temperature:", t_0, t_f)
    print("------------------------------")
    
    # Main iteration loop:
    print()
    print("Main loop")
    for i in range(schedule_split, iterations):
        rand = random.randint(0,100)
        rand = rand/100

        #Progress
        if ((i) % progress_split == 0):
            print()
            print("Iteration:", i , "| Best objective:", best_objective, "| Weights:", weights)



        #Operation choice
        op = random.choices([0, 1, 2], weights=weights)[0]
        counts[op] += 1
        if op == 0:
            candidate_solution, candidate_objective = one_reinsert(runner, incumbent_solution)
        elif op == 1:
            candidate_solution, candidate_objective = truck_section_reinsert(runner, incumbent_solution)
        else:
            candidate_solution, candidate_objective = flatten_section(runner, incumbent_solution)

        #If no insertions are found using one-reinsert, it will return none.
        if not candidate_solution:
            redundant_operators += 1
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
            rewards[op] += (improvement_reward * (1 - (t/t_0)))
            
            if incumbent_objective < best_objective:
                best_solution = copy_solution(incumbent_solution)
                best_objective = incumbent_objective
                rewards[op] += new_best_reward
                
        elif candidate_feasible and (rand <  p):
            if delta_e != 0:
                incumbent_solution = copy_solution(candidate_solution)
                incumbent_objective = candidate_objective
                rewards[op] += (sa_accept_reward * (t/t_0))
        t = alpha * t

        # Update weights every weight_split iterations
        if i % weight_split == 0:
            scores_sum = 0

            # Update scores (long term)
            for op in range(len(weights)):
                avg_reward = (rewards[op] / counts[op]) if counts[op] > 0 else 0
                scores[op] = ((1-decay) * scores[op]) + (decay * avg_reward)
                scores_sum += scores[op]

            # Update weights based on scores
            for op in range(len(weights)):
                if scores_sum > 0:
                    weights[op] = (1 - len(weights) * min_p) * (scores[op] / scores_sum) + min_p
                else:
                    weights[op] = 1 / len(weights)

            #Reset rewards and counts
            rewards = [0,0,0]
            counts = [0,0,0]
        

        #Update avg delta e for the used operator.
        avg_delta_e[op] = ((1-decay) * avg_delta_e[op]) + (decay * delta_e)

        #Update weights based on theire avg_delta_e and the gradient.
        weights = update_weights()

        
        if i % save_split == 0:
            save_to_file(filename, best_solution, best_objective, this_run_best_objective, all_time_best_objective)

    save_to_file(filename, best_solution, best_objective, this_run_best_objective, all_time_best_objective)
    return best_solution

def update_weights():
    return "yo"